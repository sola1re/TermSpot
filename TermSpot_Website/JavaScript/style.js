function sendEmail() {
    var name = document.getElementById("pseudo").value;
    var email = document.getElementById("mail").value;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "send_email.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            alert("Email envoyé avec succès !");
        }
    };
    xhr.send("name=" + name + "&email=" + email);
}
