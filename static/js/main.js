const workflowButtons = document.querySelectorAll(".workflow-step");
const workflowOutput = document.querySelector("#workflow-output");
const signupForm = document.querySelector(".signup-form");
const feedbackForm = document.querySelector(".feedback-form");
const tabButtons = document.querySelectorAll(".tab-button");
const catalogCards = document.querySelectorAll(".catalog-card");
const productButtons = document.querySelectorAll(".catalog-card button");
const cartCountNodes = document.querySelectorAll(".cart-count");
const stripeCheckoutButton = document.querySelector("#stripe-checkout-button");
const stripeCheckoutStatus = document.querySelector("#stripe-checkout-status");
const paypalStatus = document.querySelector("#paypal-status");
const checkoutPage = document.querySelector(".checkout-page");
const cartItemsContainer = document.querySelector("#cart-items");
const cartEmpty = document.querySelector("#cart-empty");
const cartEmptyCta = document.querySelector("#cart-empty-cta");
const cartItemCount = document.querySelector("#cart-item-count");
const cartSubtotal = document.querySelector("#cart-subtotal");
const cartTotal = document.querySelector("#cart-total");
const cartCheckoutLink = document.querySelector("#cart-checkout-link");
const clearCartButton = document.querySelector("#clear-cart-button");
const checkoutCartTotal = document.querySelector("#checkout-cart-total");
const checkoutCartLines = document.querySelector("#checkout-cart-lines");
const couponForm = document.querySelector(".coupon-form");
const couponCodeInput = document.querySelector("#coupon-code");
const couponStatus = document.querySelector("#coupon-status");
const removeCouponButton = document.querySelector("#remove-coupon-button");
const cartDiscountLine = document.querySelector("#cart-discount-line");
const cartDiscount = document.querySelector("#cart-discount");

const CART_STORAGE_KEY = "drivedesk_cart";
const COUPON_STORAGE_KEY = "drivedesk_coupon";
const catalogDataElement = document.querySelector("#catalog-data");
const catalogData = catalogDataElement ? JSON.parse(catalogDataElement.textContent) : [];

function getCsrfToken() {
    const cookie = document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(payload),
    });
    let data = {};
    try {
        data = await response.json();
    } catch {
        data = { error: "The server returned an unexpected checkout error." };
    }
    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }
    return data;
}

function formatCurrencyFromCents(valueCents) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
    }).format(valueCents / 100);
}

function readCart() {
    try {
        return JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "[]");
    } catch {
        return [];
    }
}

function writeCart(items) {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
}

function readCoupon() {
    try {
        return JSON.parse(localStorage.getItem(COUPON_STORAGE_KEY) || "null");
    } catch {
        return null;
    }
}

function writeCoupon(coupon) {
    if (coupon) {
        localStorage.setItem(COUPON_STORAGE_KEY, JSON.stringify(coupon));
    } else {
        localStorage.removeItem(COUPON_STORAGE_KEY);
    }
}

function cartItemCountTotal(cart) {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
}

function cartSubtotalCents(cart) {
    return cart.reduce((sum, item) => sum + item.price_cents * item.quantity, 0);
}

function couponDiscountCents(subtotalCents, coupon) {
    if (!coupon || !coupon.percent_off) {
        return 0;
    }
    return Math.min(subtotalCents, Math.round((subtotalCents * coupon.percent_off) / 100));
}

function renderCartCount() {
    const cart = readCart();
    const count = cartItemCountTotal(cart);
    cartCountNodes.forEach((node) => {
        node.textContent = String(count);
    });
}

function addProductToCart(payload) {
    const cart = readCart();
    const existing = cart.find((item) => item.slug === payload.slug);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ ...payload, quantity: 1 });
    }
    writeCart(cart);
    renderCartCount();
}

function clearCart() {
    writeCart([]);
    writeCoupon(null);
    renderCartCount();
    renderCartPage();
    renderCheckoutCartSummary();
}

function updateCartQuantity(slug, nextQuantity) {
    const cart = readCart();
    const updated = cart
        .map((item) => {
            if (item.slug !== slug) {
                return item;
            }
            return { ...item, quantity: Math.max(0, Math.min(nextQuantity, 10)) };
        })
        .filter((item) => item.quantity > 0);
    writeCart(updated);
    renderCartCount();
    renderCartPage();
}

function renderCartPage() {
    if (!cartItemsContainer || !cartItemCount || !cartSubtotal || !cartTotal || !cartCheckoutLink) {
        return;
    }

    const cart = readCart();
    const itemCount = cartItemCountTotal(cart);
    const subtotalCents = cartSubtotalCents(cart);
    let coupon = readCoupon();
    const discountCents = couponDiscountCents(subtotalCents, coupon);
    const totalCents = Math.max(0, subtotalCents - discountCents);

    cartItemsContainer.innerHTML = "";
    if (cartEmpty) {
        cartEmpty.hidden = cart.length > 0;
    }
    if (cartEmptyCta) {
        cartEmptyCta.hidden = cart.length > 0;
    }

    cart.forEach((item) => {
        const row = document.createElement("article");
        row.className = "cart-item-row";
        row.innerHTML = `
            <img src="${item.image_url}" alt="${item.name}">
            <div class="cart-item-body">
                <h2>${item.name}</h2>
                <p>${item.price}</p>
                <div class="cart-item-controls">
                    <button type="button" data-action="decrement" data-slug="${item.slug}">-</button>
                    <span>${item.quantity}</span>
                    <button type="button" data-action="increment" data-slug="${item.slug}">+</button>
                    <button type="button" data-action="remove" data-slug="${item.slug}">Remove</button>
                </div>
            </div>
            <strong>${formatCurrencyFromCents(item.price_cents * item.quantity)}</strong>
        `;
        cartItemsContainer.appendChild(row);
    });

    cartItemCount.textContent = String(itemCount);
    cartSubtotal.textContent = formatCurrencyFromCents(subtotalCents);
    cartTotal.textContent = formatCurrencyFromCents(totalCents);

    if (subtotalCents === 0 && coupon) {
        writeCoupon(null);
        coupon = null;
    }

    if (cartDiscountLine && cartDiscount) {
        const shouldShowDiscount = Boolean(coupon && discountCents > 0);
        cartDiscountLine.hidden = !shouldShowDiscount;
        cartDiscount.textContent = `-${formatCurrencyFromCents(discountCents)}`;
    }

    if (couponCodeInput && coupon) {
        couponCodeInput.value = coupon.code;
    }

    if (removeCouponButton) {
        removeCouponButton.hidden = !coupon;
    }

    if (couponStatus) {
        couponStatus.textContent = coupon ? `${coupon.code} applied: ${coupon.percent_off}% off.` : "";
    }

    if (cart.length > 0) {
        cartCheckoutLink.classList.remove("disabled-link");
        cartCheckoutLink.textContent = "Checkout Cart";
        cartCheckoutLink.href = "/checkout/cart/";
    } else {
        cartCheckoutLink.classList.add("disabled-link");
        cartCheckoutLink.textContent = "Checkout Cart";
        cartCheckoutLink.href = "/products/";
    }
}

function checkoutPayload() {
    const mode = checkoutPage?.dataset.checkoutMode || "single";
    const quantityInput = document.querySelector("#checkout-quantity");
    const basePayload = {
        customer_name: document.querySelector("#checkout-name")?.value?.trim() || "",
        customer_email: document.querySelector("#checkout-email")?.value?.trim() || "",
    };

    if (mode === "cart") {
        const cartItems = readCart().map((item) => ({
            slug: item.slug,
            quantity: item.quantity,
        }));
        return { ...basePayload, cart_items: cartItems, coupon_code: readCoupon()?.code || "" };
    }

    return {
        ...basePayload,
        slug: checkoutPage.dataset.productSlug,
        quantity: quantityInput ? Number(quantityInput.value || 1) : 1,
    };
}

function renderCheckoutCartSummary() {
    if (!checkoutPage || checkoutPage.dataset.checkoutMode !== "cart" || !checkoutCartTotal || !checkoutCartLines) {
        return;
    }

    const cart = readCart();
    const subtotal = cartSubtotalCents(cart);
    const coupon = readCoupon();
    const discount = couponDiscountCents(subtotal, coupon);
    const total = Math.max(0, subtotal - discount);
    checkoutCartTotal.textContent = formatCurrencyFromCents(total);
    checkoutCartLines.innerHTML = "";

    if (cart.length === 0) {
        checkoutCartLines.innerHTML = "<p>Your cart is empty. Please add items before checkout.</p>";
        return;
    }

    cart.forEach((item) => {
        const line = document.createElement("p");
        line.textContent = `${item.name} x ${item.quantity} — ${formatCurrencyFromCents(item.price_cents * item.quantity)}`;
        checkoutCartLines.appendChild(line);
    });
    if (coupon && discount > 0) {
        const line = document.createElement("p");
        line.textContent = `${coupon.code} discount - ${formatCurrencyFromCents(discount)}`;
        checkoutCartLines.appendChild(line);
    }
}

workflowButtons.forEach((button) => {
    button.addEventListener("click", () => {
        workflowButtons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        workflowOutput.textContent = button.dataset.detail;
    });
});

if (signupForm) {
    signupForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const button = signupForm.querySelector("button");
        const email = signupForm.querySelector("input")?.value?.trim() || "";
        if (!email) {
            return;
        }

        button.disabled = true;
        button.textContent = "Sending...";

        postJson("/api/join-updates/", { email })
            .then(() => {
                button.textContent = "Joined";
            })
            .catch(() => {
                button.disabled = false;
                button.textContent = "Join The List";
            });
    });
}

if (feedbackForm) {
    feedbackForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const button = feedbackForm.querySelector("button");
        const status = feedbackForm.querySelector(".feedback-status");
        const formData = new FormData(feedbackForm);
        const payload = {
            name: String(formData.get("name") || "").trim(),
            email: String(formData.get("email") || "").trim(),
            message: String(formData.get("message") || "").trim(),
        };

        if (!payload.name || !payload.email || !payload.message) {
            return;
        }

        button.disabled = true;
        button.textContent = "Sending...";
        if (status) {
            status.textContent = "";
        }

        postJson("/api/send-feedback/", payload)
            .then(() => {
                feedbackForm.reset();
                button.textContent = "Sent";
                if (status) {
                    status.textContent = "Thanks. Your feedback was sent.";
                }
            })
            .catch((error) => {
                button.disabled = false;
                button.textContent = "Send Feedback";
                if (status) {
                    status.textContent = error.message;
                }
            });
    });
}

tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const selectedCategory = button.dataset.category;
        tabButtons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");

        catalogCards.forEach((card) => {
            const shouldShow = selectedCategory === "All" || card.dataset.category === selectedCategory;
            card.hidden = !shouldShow;
        });
    });
});

productButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const productPayload = {
            slug: button.dataset.productSlug,
            name: button.dataset.productName,
            price_cents: Number(button.dataset.productPriceCents),
            price: button.dataset.productPrice,
            image_url: button.dataset.productImage,
        };

        addProductToCart(productPayload);
        button.textContent = "Added";
        button.disabled = true;
        setTimeout(() => {
            button.textContent = "Add To Cart";
            button.disabled = false;
        }, 850);
    });
});

if (couponForm) {
    couponForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const code = couponCodeInput?.value?.trim() || "";
        const subtotalCents = cartSubtotalCents(readCart());
        const button = couponForm.querySelector("button[type='submit']");

        if (!code || subtotalCents <= 0) {
            if (couponStatus) {
                couponStatus.textContent = subtotalCents <= 0 ? "Add an item before using a coupon." : "Enter a coupon code.";
            }
            return;
        }

        if (button) {
            button.disabled = true;
            button.textContent = "Applying...";
        }
        if (couponStatus) {
            couponStatus.textContent = "";
        }

        try {
            const coupon = await postJson("/api/coupons/validate/", {
                code,
                subtotal_cents: subtotalCents,
            });
            writeCoupon(coupon);
            renderCartPage();
            renderCheckoutCartSummary();
        } catch (error) {
            writeCoupon(null);
            renderCartPage();
            renderCheckoutCartSummary();
            if (couponStatus) {
                couponStatus.textContent = "Coupon is not valid.";
            }
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = "Apply";
            }
        }
    });
}

if (removeCouponButton) {
    removeCouponButton.addEventListener("click", () => {
        writeCoupon(null);
        if (couponCodeInput) {
            couponCodeInput.value = "";
        }
        if (couponStatus) {
            couponStatus.textContent = "";
        }
        renderCartPage();
        renderCheckoutCartSummary();
    });
}

if (stripeCheckoutButton && checkoutPage) {
    stripeCheckoutButton.addEventListener("click", async () => {
        if (checkoutPage.dataset.checkoutMode === "cart" && readCart().length === 0) {
            stripeCheckoutStatus.textContent = "Your cart is empty.";
            return;
        }
        stripeCheckoutButton.disabled = true;
        stripeCheckoutStatus.textContent = "Preparing secure checkout...";

        try {
            const data = await postJson("/api/stripe/create-checkout-session/", checkoutPayload());
            window.location.href = data.checkout_url;
        } catch (error) {
            stripeCheckoutStatus.textContent = error.message;
            stripeCheckoutButton.disabled = false;
        }
    });
}

if (window.paypal && checkoutPage) {
    window.paypal.Buttons({
        async createOrder() {
            if (checkoutPage.dataset.checkoutMode === "cart" && readCart().length === 0) {
                throw new Error("Your cart is empty.");
            }
            
            const data = await postJson("/api/paypal/create-order/", checkoutPayload());
            return data.order_id;
        },
        async onApprove(data) {
            paypalStatus.textContent = "Completing PayPal payment...";
            const result = await postJson("/api/paypal/capture-order/", {
                ...checkoutPayload(),
                order_id: data.orderID,
            });
            if (checkoutPage.dataset.checkoutMode === "cart") {
                clearCart();
            }
            window.location.href = result.redirect_url;
        },
        onError(error) {
            paypalStatus.textContent = error?.message || "PayPal checkout could not be started.";
        },
    }).render("#paypal-button-container");
}

if (cartItemsContainer) {
    cartItemsContainer.addEventListener("click", (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement)) {
            return;
        }
        const slug = target.dataset.slug;
        const action = target.dataset.action;
        if (!slug || !action) {
            return;
        }

        const cart = readCart();
        const currentItem = cart.find((item) => item.slug === slug);
        if (!currentItem) {
            return;
        }

        if (action === "increment") {
            updateCartQuantity(slug, currentItem.quantity + 1);
        } else if (action === "decrement") {
            updateCartQuantity(slug, currentItem.quantity - 1);
        } else if (action === "remove") {
            updateCartQuantity(slug, 0);
        }
    });
}

if (clearCartButton) {
    clearCartButton.addEventListener("click", () => {
        clearCart();
    });
}

if (window.location.pathname === "/checkout/success/") {
    clearCart();
}

renderCartCount();
renderCartPage();
renderCheckoutCartSummary();
