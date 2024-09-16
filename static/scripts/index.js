const uploadBtn = document.getElementById("upload-btn");
const uploadModal = document.getElementById("upload-modal");
const closeModalBtn = document.getElementById("close-modal-btn");
const message = document.querySelector(".message");
const login = document.querySelector(".login");
const logout = document.querySelector(".logout");

if (message)
  setTimeout(() => {
    message.style.display = "none";
  }, 5000);

if (login)
  login.addEventListener("click", () => {
    window.location.href = "/login";
  });

if (logout)
  logout.addEventListener("click", () => {
    window.location.href = "/logout";
  });

uploadBtn.addEventListener("click", () => {
  uploadModal.style.display = "flex";
});

closeModalBtn.addEventListener("click", () => {
  uploadModal.style.display = "none";
});

window.addEventListener("click", (event) => {
  if (event.target === uploadModal) {
    uploadModal.style.display = "none";
  }
});
