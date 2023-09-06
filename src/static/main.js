// Store token after successful login
$.post("/login", { email: "email", password: "password" }).done(function (
  data
) {
  localStorage.setItem("access_token", data.access_token);
});

// Get discoveries with JWT token
function getDiscoveries() {
  let token = localStorage.getItem("access_token");
  $.ajax({
    url: "/discoveries",
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    success: function (data) {
      console.log(data);
    },
  });
}
