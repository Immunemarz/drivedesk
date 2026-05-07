const workflowButtons = document.querySelectorAll(".workflow-step");
const workflowOutput = document.querySelector("#workflow-output");
const signupForm = document.querySelector(".signup-form");
const tabButtons = document.querySelectorAll(".tab-button");
const catalogCards = document.querySelectorAll(".catalog-card");
const productButtons = document.querySelectorAll(".catalog-card button");

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
        button.textContent = "Joined";
        button.disabled = true;
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
        button.textContent = "Added To Cart";
        button.disabled = true;
    });
});
