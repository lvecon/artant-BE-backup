from django.db.models import F, Count
from django.db.models.functions import Length
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from reviews.models import Review, ReviewImage, ReviewResponse
from . import serializers
from reviews.serializers import ReviewDetailSerializer
from products.models import Product
from shops.models import Shop


class ReviewDetails(APIView):
    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        review = self.get_object(pk)

        serializer = ReviewDetailSerializer(
            review,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk, review_pk):
        review = self.get_object(review_pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        # 페이지네이션
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.REVIEW_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        product = self.get_object(pk)
        total_reviews = product.reviews.count()
        reviews = product.reviews.all()

        # query parameter for sorting
        query_type = self.request.GET.get("sort", None)

        if query_type == "created_at":
            reviews = reviews.order_by("-created_at")
        else:  # TODO: 추천순 리뷰 정렬 기준 기획
            reviews = reviews.annotate(
                recommendation_weight=(Length("content"))
                + F("rating") * 100
                + Count("images") * 40
            )
            # 추천 가중치를 기준으로 정렬
            reviews = reviews.order_by("-recommendation_weight")

        # 최종 정렬 결과를 반환
        serializer = serializers.ReviewSerializer(
            reviews[start:end],
            many=True,
        )

        response_data = {
            "total_count": total_reviews,
            "reviews": serializer.data,
        }
        return Response(response_data)

    def post(self, request, pk):
        user = request.user
        product = self.get_object(pk)
        image_urls = request.data.get("images", [])

        serializer = serializers.ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=user,
                product=product,
            )

            if image_urls:
                images_data = [
                    {"image": url, "review": review.pk} for url in image_urls
                ]
                images_serializer = serializers.ReviewImageSerializer(
                    data=images_data, many=True
                )
                images_serializer.is_valid(raise_exception=True)
                images = images_serializer.save()

                review.images.set(images)

            serializer = serializers.ReviewSerializer(review)
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

        serializer = serializers.ReviewSerializer(
            review,
        )

        return Response(serializer.data)

    def put(self, request, pk, review_pk):
        review = self.get_object(review_pk)
        serializer = serializers.ReviewSerializer(
            review, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, review_pk):
        review = self.get_object(review_pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewResponse(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_pk):
        try:
            return Review.objects.get(pk=review_pk).reply
        except ReviewResponse.DoesNotExist:
            raise NotFound

    def get(self, request, pk, review_pk):
        reply = self.get_object(review_pk)

        serializer = serializers.ReviewResponseSerializer(
            reply,
        )

        return Response(serializer.data)

    def post(self, request, pk, review_pk):
        try:
            review = Review.objects.get(pk=review_pk)
        except Review.DoesNotExist:
            raise NotFound("Review not found.")

        # 상점 권한 확인
        if review.product.shop != request.user.shop:
            raise PermissionDenied(
                "You don't have permission to post a reply for this review."
            )
        serializer = serializers.ReviewResponseSerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(review=review, shop=request.user.shop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, review_pk):
        reply = self.get_object(review_pk)

        serializer = serializers.ReviewResponseSerializer(
            reply, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, review_pk):
        reply = self.get_object(review_pk)
        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewImageList(APIView):
    def get(self, request, product_pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.REVIEW_IMAGE_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        photos = ReviewImage.objects.filter(review__product_id=product_pk)
        serializer = serializers.ReviewImageSerializer(
            photos[start:end],
            many=True,
        )

        return Response(serializer.data)


# TODO: Reviews App 으로 리팩토링
class ShopReviews(APIView):
    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1
        query_type = self.request.GET.get("sort", None)
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        shop = self.get_object(pk)

        products = shop.products.all()
        all_reviews = []
        for product in products:
            reviews = product.reviews.all()
            all_reviews.extend(reviews)

        total_reviews = len(all_reviews)

        if query_type == "created_at":
            all_reviews_sorted = sorted(
                all_reviews, key=lambda x: x.created_at, reverse=True
            )
            serializer = serializers.ReviewSerializer(
                all_reviews_sorted[start:end],
                many=True,
            )

            response_data = {
                "total_count": total_reviews,  # 상품의 총 개수를 응답 데이터에 추가
                "reviews": serializer.data,
            }

            return Response(response_data)

        else:  # suggested
            all_reviews = sorted(
                all_reviews,
                key=lambda x: (
                    len(x.content),
                    x.rating * 100 + x.images.count() * 40,
                ),
                reverse=True,
            )
            serializer = serializers.ReviewSerializer(
                all_reviews[start:end],
                many=True,
            )

            response_data = {
                "total_count": total_reviews,
                "reviews": serializer.data,
            }
            return Response(response_data)


# TODO: Reviews App 으로 리팩토링
class ReviewPhotos(APIView):
    def get_object(self, pk):
        try:
            return Shop.objects.get(pk=pk)
        except Shop.DoesNotExist:
            raise NotFound

    def get(self, request, pk, product_pk):
        try:
            page = request.query_params.get("page", 1)  # ( ,default value)
            page = int(page)  # Type change
        except ValueError:
            page = 1

        page_size = settings.REVIEW_IMAGE_PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        shop = self.get_object(pk)
        product_name = Product.objects.get(pk=product_pk).name

        products = shop.products.all()
        all_reviews = []
        for product in products:
            reviews = product.reviews.filter(images__isnull=False)
            all_reviews.extend(reviews)

        all_reviews_sorted = sorted(
            all_reviews, key=lambda x: x.created_at, reverse=True
        )

        same_product_reviews = []
        other_reviews = []
        for review in all_reviews_sorted:
            if review.product.name == product_name:
                same_product_reviews.append(review)
            else:
                other_reviews.append(review)

        all_reviews_with_images = same_product_reviews + other_reviews

        images = [
            image.image
            for review in all_reviews_with_images
            for image in review.images.all()
        ][start:end]

        response_data = {
            "images": images,
        }
        return Response(response_data)
