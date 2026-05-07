const valueElement = document.querySelector("#drop-value");
const changeElement = document.querySelector("#drop-change");
const workflowButtons = document.querySelectorAll(".workflow-step");
const workflowOutput = document.querySelector("#workflow-output");
const signupForm = document.querySelector(".signup-form");

let dropRevenue = 12400;

function formatCurrency(value) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
    }).format(value);
}

setInterval(() => {
    const movement = Math.floor(Math.random() * 420) + 89;
    dropRevenue += movement;
    valueElement.textContent = formatCurrency(dropRevenue);
    const positive = movement >= 0;
    changeElement.textContent = `${positive ? "+" : ""}${movement.toLocaleString()} in reserved kits`;
    changeElement.style.color = positive ? "#8fd3ff" : "#e48272";
}, 2800);

workflowButtons.forEach((button) => {
    button.addEventListener("click", () => {
        workflowButtons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        workflowOutput.textContent = button.dataset.detail;
    });
});

signupForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const button = signupForm.querySelector("button");
    button.textContent = "Kit Reserved";
    button.disabled = true;
});
