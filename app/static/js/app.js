console.log("Frontend JS loaded!");


document.getElementById("signup-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch("/user/signup", {
        method: "POST",
        body: formData,
    });
    if (response.redirected) {
        window.location.href = response.url;
    }
});