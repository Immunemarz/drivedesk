const valueElement = document.querySelector("#market-value");
const changeElement = document.querySelector("#market-change");
const ritualButtons = document.querySelectorAll(".ritual");
const ritualOutput = document.querySelector("#ritual-output");
const signupForm = document.querySelector(".signup-form");

let portfolioValue = 284920;

function formatCurrency(value) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
    }).format(value);
}

setInterval(() => {
    const movement = Math.floor(Math.random() * 1800) - 520;
    portfolioValue += movement;
    valueElement.textContent = formatCurrency(portfolioValue);
    const positive = movement >= 0;
    changeElement.textContent = `${positive ? "+" : ""}${movement.toLocaleString()} live move`;
    changeElement.style.color = positive ? "#7bc99b" : "#e48272";
}, 2600);

ritualButtons.forEach((button) => {
    button.addEventListener("click", () => {
        ritualButtons.forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        ritualOutput.textContent = button.dataset.ritual;
    });
});

signupForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const button = signupForm.querySelector("button");
    button.textContent = "Access Requested";
    button.disabled = true;
});
