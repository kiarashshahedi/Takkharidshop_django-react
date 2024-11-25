from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Payment
from orders.models import Order
from .serializers import PaymentSerializer


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        order_id = data.get('order_id')
        payment_method = data.get('method')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'Pending':
            return Response({"error": "Payment already completed for this order."},
                            status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            method=payment_method,
            amount=order.total_amount
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        transaction_id = data.get('transaction_id')
        payment_id = data.get('payment_id')

        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if transaction_id:
            payment.mark_as_completed(transaction_id=transaction_id)
            return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)

        payment.mark_as_failed()
        return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        return Response(PaymentSerializer(payments, many=True).data)
