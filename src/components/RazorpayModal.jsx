import { useState } from 'react'
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  CreditCard,
  Download,
  Package,
  QrCode,
  ShieldCheck,
  Sparkles,
  Truck,
  Wallet,
  X,
} from 'lucide-react'
import { useCart } from '../context/CartContext'

export default function RazorpayModal() {
  const {
    isRazorpayOpen,
    setIsRazorpayOpen,
    items,
    offerProgress,
    recordOrder,
    lastPlacedOrder,
    setLastPlacedOrder,
  } = useCart()

  const [paymentMethod, setPaymentMethod] = useState('upi')
  const [upiId, setUpiId] = useState('shopper@oksbi')
  const [cardNumber, setCardNumber] = useState('4111 2222 3333 4444')
  const [cardExpiry, setCardExpiry] = useState('12/28')
  const [cardCvv, setCardCvv] = useState('789')
  const [bank, setBank] = useState('HDFC Bank')
  const [isProcessing, setIsProcessing] = useState(false)
  const [orderConfirmed, setOrderConfirmed] = useState(false)

  if (!isRazorpayOpen && !orderConfirmed) return null

  const handlePay = () => {
    setIsProcessing(true)
    setTimeout(() => {
      setIsProcessing(false)
      const order = recordOrder({
        method: paymentMethod.toUpperCase(),
        paymentId: `pay_test_${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      })
      setOrderConfirmed(true)
    }, 1800)
  }

  const handleClose = () => {
    setIsRazorpayOpen(false)
    setOrderConfirmed(false)
    setLastPlacedOrder(null)
  }

  // If order was confirmed, show the Order Receipt & Tracking Screen
  if (orderConfirmed && lastPlacedOrder) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div className="relative max-h-[92vh] overflow-y-auto max-w-lg w-full rounded-3xl bg-white p-6 sm:p-8 shadow-2xl text-center">
          <button
            onClick={handleClose}
            className="absolute right-4 top-4 rounded-full bg-slate-100 p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
          >
            <X className="h-4 w-4" />
          </button>

          {/* Success Checkmark */}
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 mb-4 animate-bounce">
            <CheckCircle2 className="h-9 w-9" />
          </div>

          <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
            Payment Verified via Razorpay Test
          </span>

          <h2 className="mt-2 text-2xl font-black text-slate-900">Order Placed Successfully!</h2>
          <p className="text-xs text-slate-500 mt-1">
            Order ID: <span className="font-mono font-bold text-slate-800">{lastPlacedOrder.orderId}</span>
          </p>

          {/* Order Tracking Timeline */}
          <div className="mt-6 rounded-2xl bg-slate-50 p-4 border border-slate-100 text-left">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3">Live Order Tracking</p>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-white flex-shrink-0 text-xs">
                  ✓
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900">Payment Confirmed</p>
                  <p className="text-[11px] text-slate-500">Ref: {lastPlacedOrder.paymentId}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-violet-600 text-white flex-shrink-0 animate-pulse text-xs">
                  <Package className="h-3 w-3" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900">Packing at Central Warehouse</p>
                  <p className="text-[11px] text-slate-500">Expected to dispatch in 2 hours</p>
                </div>
              </div>

              <div className="flex items-start gap-3 opacity-60">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-200 text-slate-500 flex-shrink-0 text-xs">
                  <Truck className="h-3 w-3" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-700">Express Delivery</p>
                  <p className="text-[11px] text-slate-400">{lastPlacedOrder.deliveryEstimate}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Ordered items breakdown */}
          <div className="mt-4 rounded-2xl border border-slate-200 p-3.5 text-left max-h-44 overflow-y-auto space-y-2">
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wide">Ordered Items ({lastPlacedOrder.items.length})</p>
            {lastPlacedOrder.items.map(item => (
              <div key={item.product_id} className="flex items-center justify-between text-xs py-1 border-b border-slate-50 last:border-0">
                <div className="flex items-center gap-2 truncate">
                  <span className="font-semibold text-slate-800 truncate">{item.name}</span>
                  <span className="text-slate-400">×{item.quantity}</span>
                </div>
                <span className="font-bold text-slate-900 flex-shrink-0">
                  ₹{(item.price * item.quantity).toLocaleString('en-IN')}
                </span>
              </div>
            ))}
          </div>

          {/* Total Paid */}
          <div className="mt-4 flex items-center justify-between rounded-xl bg-violet-50 px-4 py-3">
            <span className="text-xs font-bold text-violet-900">Total Paid</span>
            <span className="text-lg font-black text-violet-950">₹{lastPlacedOrder.total.toLocaleString('en-IN')}</span>
          </div>

          <div className="mt-6 flex gap-2">
            <button
              onClick={handleClose}
              className="flex-1 rounded-2xl bg-slate-900 py-3 text-xs font-bold text-white hover:bg-slate-800 transition"
            >
              Continue Shopping
            </button>
            <button
              onClick={() => alert(`Invoice downloaded for Order: ${lastPlacedOrder.orderId}`)}
              className="inline-flex items-center gap-1.5 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              <Download className="h-3.5 w-3.5" /> Invoice
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Payment Checkout Modal
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative max-h-[92vh] overflow-y-auto max-w-md w-full rounded-3xl bg-white p-6 shadow-2xl">
        <button
          onClick={handleClose}
          className="absolute right-4 top-4 rounded-full bg-slate-100 p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Razorpay Brand Header */}
        <div className="flex items-center gap-2 mb-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#0c2340] text-white font-black text-sm">
            R
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-black text-[#0c2340] tracking-tight">Razorpay</span>
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[9px] font-bold text-amber-800">
                TEST MODE
              </span>
            </div>
            <p className="text-[10px] text-slate-400">ShopSense AI Checkout</p>
          </div>
        </div>

        {/* Total Banner */}
        <div className="mb-4 rounded-2xl bg-gradient-to-r from-slate-900 to-indigo-950 p-4 text-white">
          <p className="text-[10px] font-medium text-slate-300 uppercase tracking-wider">Amount Payable</p>
          <div className="flex items-baseline justify-between mt-1">
            <h3 className="text-2xl font-black">₹{offerProgress.grandTotal.toLocaleString('en-IN')}</h3>
            {offerProgress.discountAmount > 0 && (
              <span className="text-xs font-semibold text-emerald-400">
                You saved ₹{offerProgress.discountAmount.toLocaleString('en-IN')}!
              </span>
            )}
          </div>
        </div>

        {/* Payment Methods Tabs */}
        <div className="mb-4 grid grid-cols-3 gap-1.5 rounded-xl bg-slate-100 p-1 text-xs font-semibold text-slate-600">
          <button
            type="button"
            onClick={() => setPaymentMethod('upi')}
            className={`flex items-center justify-center gap-1.5 rounded-lg py-2 transition ${
              paymentMethod === 'upi' ? 'bg-white text-violet-700 shadow-sm' : 'hover:text-slate-900'
            }`}
          >
            <QrCode className="h-3.5 w-3.5" /> UPI / QR
          </button>
          <button
            type="button"
            onClick={() => setPaymentMethod('card')}
            className={`flex items-center justify-center gap-1.5 rounded-lg py-2 transition ${
              paymentMethod === 'card' ? 'bg-white text-violet-700 shadow-sm' : 'hover:text-slate-900'
            }`}
          >
            <CreditCard className="h-3.5 w-3.5" /> Cards
          </button>
          <button
            type="button"
            onClick={() => setPaymentMethod('netbanking')}
            className={`flex items-center justify-center gap-1.5 rounded-lg py-2 transition ${
              paymentMethod === 'netbanking' ? 'bg-white text-violet-700 shadow-sm' : 'hover:text-slate-900'
            }`}
          >
            <Building2 className="h-3.5 w-3.5" /> Netbanking
          </button>
        </div>

        {/* Payment Form by Tab */}
        <div className="space-y-3 mb-5">
          {paymentMethod === 'upi' && (
            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-slate-600">UPI ID / VPA</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={upiId}
                  onChange={e => setUpiId(e.target.value)}
                  placeholder="username@okhdfcbank"
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs outline-none focus:border-violet-500"
                />
              </div>
              <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-400">
                <span className="rounded bg-slate-100 px-2 py-0.5">Google Pay</span>
                <span className="rounded bg-slate-100 px-2 py-0.5">PhonePe</span>
                <span className="rounded bg-slate-100 px-2 py-0.5">Paytm</span>
              </div>
            </div>
          )}

          {paymentMethod === 'card' && (
            <div className="space-y-2.5">
              <div>
                <label className="text-[11px] font-semibold text-slate-600">Test Card Number</label>
                <input
                  type="text"
                  value={cardNumber}
                  onChange={e => setCardNumber(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-mono outline-none focus:border-violet-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] font-semibold text-slate-600">Expiry (MM/YY)</label>
                  <input
                    type="text"
                    value={cardExpiry}
                    onChange={e => setCardExpiry(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-mono outline-none focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-slate-600">CVV</label>
                  <input
                    type="password"
                    maxLength={3}
                    value={cardCvv}
                    onChange={e => setCardCvv(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-mono outline-none focus:border-violet-500"
                  />
                </div>
              </div>
              <p className="text-[10px] text-slate-400">Pre-filled with Razorpay test card credentials.</p>
            </div>
          )}

          {paymentMethod === 'netbanking' && (
            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-slate-600">Select Bank</label>
              <select
                value={bank}
                onChange={e => setBank(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs outline-none focus:border-violet-500"
              >
                <option value="HDFC Bank">HDFC Bank</option>
                <option value="ICICI Bank">ICICI Bank</option>
                <option value="State Bank of India">State Bank of India (SBI)</option>
                <option value="Axis Bank">Axis Bank</option>
                <option value="Kotak Mahindra Bank">Kotak Mahindra Bank</option>
              </select>
            </div>
          )}
        </div>

        {/* Security Notice */}
        <div className="mb-4 flex items-center gap-2 rounded-xl bg-slate-50 p-2.5 text-[11px] text-slate-500 border border-slate-100">
          <ShieldCheck className="h-4 w-4 text-emerald-600 flex-shrink-0" />
          <span>Simulated environment: No actual debit will occur from your bank account.</span>
        </div>

        {/* Pay Button */}
        <button
          type="button"
          disabled={isProcessing}
          onClick={handlePay}
          className="w-full flex items-center justify-center gap-2 rounded-2xl bg-[#0c2340] py-3.5 text-sm font-bold text-white hover:bg-[#15345d] transition shadow-md disabled:opacity-60"
        >
          {isProcessing ? (
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              <span>Verifying with Razorpay...</span>
            </div>
          ) : (
            <span>Authorize Payment of ₹{offerProgress.grandTotal.toLocaleString('en-IN')}</span>
          )}
        </button>
      </div>
    </div>
  )
}
