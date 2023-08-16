class OrderStatus:
    DRAFT = "draft"  # fully editable, not finalized order created by staff users
    UNCONFIRMED = (
        "unconfirmed"  # order created by customers when confirmation is required
    )
    UNFULFILLED = "unfulfilled"  # order with no items marked as fulfilled
    PARTIALLY_FULFILLED = (
        "partially fulfilled"  # order with some items marked as fulfilled
    )
    FULFILLED = "fulfilled"  # order with all items marked as fulfilled

    PARTIALLY_RETURNED = (
        "partially_returned"  # order with some items marked as returned
    )
    RETURNED = "returned"  # order with all items marked as returned
    CANCELED = "canceled"  # permanently canceled order
    EXPIRED = "expired"  # order marked as expired

    CHOICES = [
        (DRAFT, "Draft"),
        (UNCONFIRMED, "Unconfirmed"),
        (UNFULFILLED, "Unfulfilled"),
        (PARTIALLY_FULFILLED, "Partially fulfilled"),
        (PARTIALLY_RETURNED, "Partially returned"),
        (RETURNED, "Returned"),
        (FULFILLED, "Fulfilled"),
        (CANCELED, "Canceled"),
        (EXPIRED, "Expired"),
    ]
