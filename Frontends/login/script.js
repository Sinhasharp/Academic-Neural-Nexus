function showForm(form) {
    let forms = document.querySelectorAll(".Form");
    forms.forEach(f => f.style.display = "none");

    if (form === "main") {
        document.querySelector(".select-login").style.display = "flex";
    } else {
        document.getElementById(form + "-form").style.display = "flex";
    }
}

// Show the initial "Login As" page
showForm("main");
