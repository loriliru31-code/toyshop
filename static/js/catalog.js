document.addEventListener("DOMContentLoaded", () => {
    // Элементы фильтра и сетки каталога
    const catalogGrid = document.querySelector(".catalog-products-grid");
    const categorySelect = document.getElementById("categorySelect");
    const applyBtn = document.querySelector(".apply-btn");

    // Функция загрузки товаров по категории
    const loadProducts = (categoryId = "") => {
        let url = "/api/products";
        if (categoryId) {
            url += `?category_id=${categoryId}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(products => {
                catalogGrid.innerHTML = ""; // очищаем сетку
                products.forEach(p => {
                    const card = document.createElement("article");
                    card.className = "product-card";
                    card.innerHTML = `
                        <a href="/product/${p.id}" class="product-link">
                            <div class="product-img">
                                ${p.images ? `<img src="${p.images}" alt="${p.name}">` : '<div class="placeholder-img"></div>'}
                            </div>
                            <p class="product-title">${p.name}</p>
                            <p class="product-price">${p.price} ₽</p>
                        </a>

                        <button 
                            class="btn-cart add-to-cart"
                            data-id="${p.id}"
                            type="button"
                        >
                            В корзину
                        </button>
                    `;
                    catalogGrid.appendChild(card);
                });
            })
            .catch(err => {
                catalogGrid.innerHTML = "<p>Ошибка загрузки товаров</p>";
                console.error("Ошибка загрузки товаров:", err);
            });
    };

    // Получаем category_id из URL (для фильтрации при переходе по ссылке)
    const urlParams = new URLSearchParams(window.location.search);
    const categoryId = urlParams.get("category_id") || "";

    // Если есть category_id, устанавливаем его в селект
    if (categorySelect && categoryId) {
        categorySelect.value = categoryId;
    }

    // Загружаем товары сразу при открытии страницы
    loadProducts(categoryId);

    // Обработка кнопки "Применить"
    if (applyBtn) {
        applyBtn.addEventListener("click", () => {
            const selectedCategory = categorySelect.value;
            loadProducts(selectedCategory);

            // Обновляем URL без перезагрузки страницы
            const newUrl = selectedCategory ? `/catalog?category_id=${selectedCategory}` : "/catalog";
            window.history.replaceState(null, "", newUrl);
        });
    }
});