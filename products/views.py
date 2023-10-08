from django.conf import settings
from django.shortcuts import render
import requests
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from products import serializers
from users.models import Shop
from products.models import Product, UserProductTimestamp
from reviews.models import Review, ReviewReply
from products.models import Category
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.utils.timezone import now
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from django.db.models import F, Count
from reviews.serializers import (
    ReviewSerializer,
    ReviewPhotoSerializer,
    ReviewDetailSerializer,
    ReviewReplySerializer,
)
from django.db.models.functions import Length
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ProductImage, ProductVideo
from rest_framework.status import HTTP_200_OK
from reviews.models import ReviewPhoto


# Create your views here.
class Products(APIView):
    def get(self, request):
        color_param = self.request.GET.get("color", None)
        colors = color_param.split(",") if color_param else []
        limit = int(self.request.GET.get("limit", 40))
        offset = int(self.request.GET.get("offset", 0))
        category_type = self.request.GET.get("category", None)
        tag = self.request.GET.get("tag", None)

        price_upper_range = self.request.GET.get("PriceUpper", 10000000)
        price_lower_range = self.request.GET.get("PriceLower", 0)
        search = self.request.GET.get("search", None)
        query_type = self.request.GET.get("sort", None)

        q = Q()

        if colors:
            q &= Q(colors__name__in=colors)
        if category_type and category_type != "모든작품":
            q &= Q(category__name=category_type)
        if tag:
            q &= Q(tags__tag=tag)

        if price_lower_range != 0 or price_upper_range != 10000000:
            q &= Q(price__range=(price_lower_range, price_upper_range))

        if search:
            q &= (
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(shop__shop_name__exact=search)
                | Q(colors__name__exact=search)
            )

        products = Product.objects.filter(q).distinct()
        total_products = products.count()

        if query_type == "created_at":
            products = products.order_by("-created_at")[offset : offset + limit]
            serializer = serializers.ProductListSerializer(
                products,
                many=True,
                context={"request": request},
            )
            response_data = {
                "total_count": total_products,
                "products": serializer.data,
            }
            return Response(response_data)
        elif query_type == "price_asc":
            products = products.order_by("price")[offset : offset + limit]
            serializer = serializers.ProductListSerializer(
                products,
                many=True,
                context={"request": request},
            )
            response_data = {
                "total_count": total_products,
                "products": serializer.data,
            }
            return Response(response_data)
        elif query_type == "price_desc":
            products = products.order_by("-price")[offset : offset + limit]
            serializer = serializers.ProductListSerializer(
                products,
                many=True,
                context={"request": request},
            )
            response_data = {
                "total_count": total_products,
                "products": serializer.data,
            }
            return Response(response_data)
        elif query_type == "discount_desc":
            products = products.annotate(
                discount_rate=(1 - (F("price") * 1.0 / F("original_price"))) * 100
            )
            products = products.order_by("-discount_rate")[offset : offset + limit]
            serializer = serializers.ProductListSerializer(
                products,
                many=True,
                context={"request": request},
            )
            response_data = {
                "total_count": total_products,
                "products": serializer.data,
            }
            return Response(response_data)
        elif query_type == "review_desc":
            products = products.annotate(review_count=Count("reviews")).order_by(
                "-review_count"
            )[offset : offset + limit]

            serializer = serializers.ProductListSerializer(
                products,
                many=True,
                context={"request": request},
            )

            response_data = {
                "total_count": total_products,
                "products": serializer.data,
            }

            return Response(response_data)
        else:
            products = products.order_by("-order_count")[offset : offset + limit]
            serializer = serializers.ProductListSerializer(
                products,
                many=True,
                context={"request": request},
            )
            response_data = {
                "total_count": total_products,  # 상품의 총 개수를 응답 데이터에 추가
                "products": serializer.data,
            }
            return Response(response_data)


class ProductDetails(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def user_viewed(self, timestamp, product):
        user = self.request.user
        if not user.is_authenticated:
            return
        upt, _ = UserProductTimestamp.objects.get_or_create(user=user, product=product)
        upt.timestamp = timestamp
        upt.save()
        return upt.timestamp

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        product = self.get_object(pk)
        self.user_viewed(now(), product)
        serializer = serializers.ProductDetailSerializer(
            product,
            context={"reqeust": request},
        )
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        # if product.shop.user != request.user:
        #     raise PermissionDenied
        serializer = serializers.ProductDetailSerializer(
            product,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_product = serializer.save()
            return Response(
                serializers.ProductDetailSerializer(updated_product).data,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        product = self.get_object(pk)
        # if product.shop.user != request.user:
        #     raise PermissionDenied
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecentlyViewed(APIView):
    def get(self, request):
        user = request.user
        recently_viewed_timestamps = UserProductTimestamp.objects.filter(
            user=user.pk
        ).order_by("-timestamp")[:10]
        recently_viewed_products = [
            timestamp.product for timestamp in recently_viewed_timestamps
        ]

        serializer = serializers.ProductListSerializer(
            recently_viewed_products,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class ProductReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        query_type = self.request.GET.get("sort", None)

        page_size = settings.REVIEW_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        product = self.get_object(pk)
        total_reviews = product.reviews.count()
        reviews = product.reviews.all()

        if query_type == "created_at":
            reviews = reviews.order_by("-created_at")
            serializer = ReviewSerializer(
                reviews[start:end],
                many=True,
            )

            response_data = {
                "total_count": total_reviews,  # 상품의 총 개수를 응답 데이터에 추가
                "reviews": serializer.data,
            }
            return Response(response_data)

        else:  # suggested
            reviews = reviews.annotate(
                recommendation_weight=(Length("content"))
                + F("rating") * 100
                + Count("images") * 40
            )

            # 추천 가중치를 기준으로 정렬
            reviews = reviews.order_by("-recommendation_weight")

            # 최종 정렬 결과를 반환
            serializer = ReviewSerializer(
                reviews[start:end],
                many=True,
            )

            response_data = {
                "total_count": reviews.count(),
                "reviews": serializer.data,
            }
            return Response(response_data)

    def post(self, request, pk):
        user = request.user
        product = self.get_object(pk)
        image_urls = request.data.get("images", [])

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=user,
                product=product,
            )

            if image_urls:
                images_data = [
                    {"image": url, "review": review.pk} for url in image_urls
                ]
                images_serializer = ReviewPhotoSerializer(data=images_data, many=True)
                images_serializer.is_valid(raise_exception=True)
                images = images_serializer.save()

                review.images.set(images)

            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ProductReviewDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_pk):
        try:
            return Review.objects.get(pk=review_pk)
        except Product.DoesNotExist:
            raise NotFound

    def get(self, request, pk, review_pk):
        review = self.get_object(review_pk)

        serializer = ReviewSerializer(
            review,
        )

        return Response(serializer.data)

    def put(self, request, pk, review_pk):
        review = self.get_object(review_pk)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, review_pk):
        review = self.get_object(review_pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewReply(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_pk):
        try:
            return Review.objects.get(pk=review_pk).reply
        except ReviewReply.DoesNotExist:
            raise NotFound

    def get(self, request, pk, review_pk):
        reply = self.get_object(review_pk)

        serializer = ReviewReplySerializer(
            reply,
        )

        return Response(serializer.data)

    def post(self, request, pk, review_pk):
        review = Review.objects.get(pk=review_pk)
        user_shops = request.user.shop.all()
        try:
            matching_shop = user_shops.get(pk=review.product.shop.pk)
        except:
            return Response(
                {"error": "You don't have permission to post a reply for this review."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReviewReplySerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(review=review, shop=matching_shop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, review_pk):
        reply = self.get_object(review_pk)

        serializer = ReviewReplySerializer(reply, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, review_pk):
        reply = self.get_object(review_pk)
        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhotoDetail(APIView):
    permission_classes = [IsAuthenticated]  # check user authenticated

    def get_object(self, pk):
        try:
            return ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            raise NotFound

    def delete(self, request, pk):
        photo = self.get_object(pk)
        # if (photo.product and photo.product.owner != request.user) or (
        #     photo.experience and photo.experience.host != request.user
        # ):
        #     raise PermissionDenied
        photo.delete()
        return Response(status=HTTP_200_OK)


class GetUploadURL(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v2/direct_upload"

        one_time_url = requests.post(
            url,
            headers={"Authorization": f"Bearer {settings.CF_TOKEN}"},
        )
        one_time_url = one_time_url.json()
        result = one_time_url.get("result")
        return Response({"uploadURL": result.get("uploadURL")})


class GetVideoUploadURL(APIView):
    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/stream/direct_upload"

        payload = {"maxDurationSeconds": 60}

        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {settings.CF_TOKEN}"},
                json=payload,  # Use json parameter to send JSON data in the request body
            )
            response_data = response.json()
            if response.status_code == 200:
                upload_url = response_data.get("result", {}).get("uploadURL")
                if upload_url:
                    return Response({"uploadURL": upload_url})
                else:
                    return Response(
                        {"error": "Failed to retrieve upload URL"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return Response(response_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Request to Cloudflare failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductImages(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        product = self.get_object(pk)

        # if request.user != room.owner:
        #     raise PermissionDenied
        serializer = serializers.PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(product=product)  # connect to room
            serializer = serializers.PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ProductVideos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        product = self.get_object(pk)

        # if request.user != room.owner:
        #     raise PermissionDenied
        serializer = serializers.VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save(product=product)  # connect to room
            serializer = serializers.VideoSerializer(video)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ReviewPhotoList(APIView):
    def get(self, request, product_pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.REVIEW_IMAGE_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        photos = ReviewPhoto.objects.filter(review__product_id=product_pk)
        serializer = ReviewPhotoSerializer(
            photos[start:end],
            many=True,
        )

        return Response(serializer.data)
