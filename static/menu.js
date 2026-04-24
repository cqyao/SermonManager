function toggleMenu() {
  var x = document.getElementById("sideNav");
    if (x.style.width === "0px") {
      x.style.width = "50%"
    } else {
      x.style.width = "0px"
    }
}