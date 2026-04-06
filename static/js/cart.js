document.addEventListener("DOMContentLoaded", () => {

  // ================= ДОБАВЛЕНИЕ (через делегирование) =================
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".add-to-cart");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    const productId = btn.dataset.id;

    fetch(`/add_to_cart/${productId}`, {
        method: "POST"
    })
    .then(res => {
        if (res.status === 401) {
            showAuthMessage();
            return null;
        }
        return res.json();
    })
    .then(data => {
        if (!data) return;

        if (data.success) {
            btn.textContent = "✓ В корзине";
            btn.disabled = true;
            btn.classList.add("in-cart");

            updateCartCounter(data.cart_count);
        }
    })
    .catch(err => console.error(err));
  });


  // ================= МИНУС =================
  document.querySelectorAll(".minus").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.closest(".cart-item").dataset.id;

      fetch(`/remove_from_cart/${id}`, { method: "POST" })
        .then(res => {
          if (res.status === 401) {
            showAuthMessage();
            return null;
          }
          return res.json();
        })
        .then(data => {
          if (!data) return;

          updateCartCounter(data.cart_count);
          location.reload();
        });
    });
  });


  // ================= ПЛЮС =================
  document.querySelectorAll(".plus").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.closest(".cart-item").dataset.id;

      fetch(`/add_to_cart/${id}`, { method: "POST" })
        .then(res => {
          if (res.status === 401) {
            showAuthMessage();
            return null;
          }
          return res.json();
        })
        .then(data => {
          if (!data) return;

          updateCartCounter(data.cart_count);
          location.reload();
        });
    });
  });


  // ================= УДАЛЕНИЕ =================
  document.querySelectorAll(".remove").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.closest(".cart-item").dataset.id;

      fetch(`/remove_from_cart/${id}`, { method: "POST" })
        .then(res => {
          if (res.status === 401) {
            showAuthMessage();
            return null;
          }
          return res.json();
        })
        .then(data => {
          if (!data) return;

          updateCartCounter(data.cart_count);
          location.reload();
        });
    });
  });


  // ================= ОЧИСТКА =================
  document.getElementById("clearCart")?.addEventListener("click", () => {
    fetch("/clear_cart", { method: "POST" })
      .then(res => {
        if (res.status === 401) {
          showAuthMessage();
          return null;
        }
        return res.json();
      })
      .then(data => {
        if (!data) return;

        updateCartCounter(data.cart_count);
        location.reload();
      });
  });

});


// ================= СЧЕТЧИК =================
function updateCartCounter(count) {
  const el = document.getElementById("cart-count");
  if (el) {
    el.textContent = count;
  }
}


// ================= POPUP =================
function showAuthMessage() {
  const popup = document.getElementById("auth-popup");
  if (!popup) return;

  popup.classList.remove("hidden");

  // закрытие по клику вне окна
  popup.addEventListener("click", (e) => {
    if (e.target === popup) {
      popup.classList.add("hidden");
    }
  });
}