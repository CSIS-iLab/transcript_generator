submitted = document.getElementById("submitted");

document.getElementById("upload_submit").addEventListener("click", function () {
  document.getElementById("upload_submit").classList.add("sr-only");
  submitted.classList.remove("submitted-hidden");
  submitted.classList.add("submitted-visible");
  return console.log("upload click me");
});
