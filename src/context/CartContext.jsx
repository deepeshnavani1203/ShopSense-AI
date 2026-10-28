import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const CartContext = createContext(null)

const CART_STORAGE_KEY = 'shopsense-cart'
const ORDERS_STORAGE_KEY = 'shopsense-orders'

// Smart Cart Offer Milestones
export const OFFER_MILESTONES = [
  { threshold: 999, id: 'free_delivery', title: 'Free Express Delivery', desc: 'Free same-day/express delivery unlocked', discount: 99, isShipping: true },
  { threshold: 2500, id: 'flat_250', title: 'Flat ₹250 Instant Discount', desc: 'Auto-applied on orders above ₹2,500', discount: 250, isDiscount: true },
  { threshold: 5000, id: 'tier_10pct', title: '10% OFF + Free Tech Gift', desc: '10% off entire order + Free Cleaning Kit', discountPct: 0.10, isGift: true },
  { threshold: 15000, id: 'vip_1500', title: 'VIP Flat ₹1,500 OFF', desc: 'Mega savings for high-value orders', discount: 1500, isDiscount: true },
]

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    try {
      const stored = localStorage.getItem(CART_STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })

  const [orders, setOrders] = useState(() => {
    try {
      const stored = localStorage.getItem(ORDERS_STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })

  const [isCartOpen, setIsCartOpen] = useState(false)
  const [activeBattleProducts, setActiveBattleProducts] = useState(null)
  const [isRazorpayOpen, setIsRazorpayOpen] = useState(false)
  const [lastPlacedOrder, setLastPlacedOrder] = useState(null)

  useEffect(() => {
    try {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items))
    } catch {}
  }, [items])

  useEffect(() => {
    try {
      localStorage.setItem(ORDERS_STORAGE_KEY, JSON.stringify(orders))
    } catch {}
  }, [orders])

  const addToCart = (product, quantity = 1) => {
    if (!product || !product.product_id) return
    setItems(prev => {
      const existing = prev.find(i => i.product_id === product.product_id)
      if (existing) {
        return prev.map(i =>
          i.product_id === product.product_id ? { ...i, quantity: i.quantity + quantity } : i
        )
      }
      return [
        ...prev,
        {
          product_id: product.product_id,
          name: product.name,
          brand: product.brand,
          category: product.category,
          subcategory: product.subcategory,
          price: Number(product.price) || 0,
          currency: product.currency || 'INR',
          image: product.image,
          quantity,
          attributes: product.attributes || {},
        },
      ]
    })
    setIsCartOpen(true)
  }

  const removeFromCart = (productId) => {
    setItems(prev => prev.filter(i => i.product_id !== productId))
  }

  const updateQuantity = (productId, newQty) => {
    if (newQty <= 0) {
      removeFromCart(productId)
      return
    }
    setItems(prev =>
      prev.map(i => (i.product_id === productId ? { ...i, quantity: newQty } : i))
    )
  }

  const clearCart = () => setItems([])

  // Financial calculations
  const totalItemsCount = useMemo(() => {
    return items.reduce((sum, item) => sum + item.quantity, 0)
  }, [items])

  const subtotal = useMemo(() => {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  }, [items])

  // Offer progress calculation
  const offerProgress = useMemo(() => {
    // Find next unlocked and upcoming milestones
    let unlockedMilestone = null
    let nextMilestone = null

    for (const m of OFFER_MILESTONES) {
      if (subtotal >= m.threshold) {
        unlockedMilestone = m
      } else if (!nextMilestone) {
        nextMilestone = m
      }
    }

    const remainingToNext = nextMilestone ? Math.max(0, nextMilestone.threshold - subtotal) : 0
    const progressPercent = nextMilestone
      ? Math.min(100, Math.round((subtotal / nextMilestone.threshold) * 100))
      : 100

    let discountAmount = 0
    let freeDelivery = subtotal >= 999
    let freeGift = subtotal >= 5000

    if (subtotal >= 15000) {
      discountAmount = 1500
    } else if (subtotal >= 5000) {
      discountAmount = Math.round(subtotal * 0.10)
    } else if (subtotal >= 2500) {
      discountAmount = 250
    }

    const deliveryFee = freeDelivery || subtotal === 0 ? 0 : 99
    const grandTotal = Math.max(0, subtotal - discountAmount + deliveryFee)

    return {
      unlockedMilestone,
      nextMilestone,
      remainingToNext,
      progressPercent,
      discountAmount,
      deliveryFee,
      freeDelivery,
      freeGift,
      grandTotal,
    }
  }, [subtotal])

  const recordOrder = (orderData) => {
    const newOrder = {
      orderId: `ORD-${Date.now().toString(36).toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`,
      createdAt: new Date().toISOString(),
      items: [...items],
      subtotal,
      discount: offerProgress.discountAmount,
      deliveryFee: offerProgress.deliveryFee,
      total: offerProgress.grandTotal,
      freeGift: offerProgress.freeGift,
      paymentMethod: orderData.method || 'Razorpay Test',
      paymentId: orderData.paymentId || `pay_test_${Math.random().toString(36).substring(2, 11)}`,
      status: 'Confirmed',
      deliveryEstimate: 'Tomorrow by 8:00 PM',
      shippingAddress: orderData.address || {
        fullName: 'Demo Shopper',
        phone: '+91 98765 43210',
        line1: '402, Sunset High Street, Koramangala',
        city: 'Bengaluru',
        pincode: '560034',
      },
    }
    setOrders(prev => [newOrder, ...prev])
    setLastPlacedOrder(newOrder)
    clearCart()
    return newOrder
  }

  return (
    <CartContext.Provider
      value={{
        items,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        totalItemsCount,
        subtotal,
        offerProgress,
        isCartOpen,
        setIsCartOpen,
        activeBattleProducts,
        setActiveBattleProducts,
        isRazorpayOpen,
        setIsRazorpayOpen,
        orders,
        recordOrder,
        lastPlacedOrder,
        setLastPlacedOrder,
      }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
