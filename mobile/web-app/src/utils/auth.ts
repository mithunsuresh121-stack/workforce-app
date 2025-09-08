export function getAuthToken() {
  const token = localStorage.getItem("authToken");
  console.log("getAuthToken:", token);
  return token;
}

export function setAuthToken(token: string) {
  console.log("setAuthToken:", token);
  localStorage.setItem("authToken", token);
}

export function clearAuthToken() {
  console.log("clearAuthToken");
  localStorage.removeItem("authToken");
  localStorage.removeItem("userProfile");
}

export function getUserProfile() {
  const profile = localStorage.getItem("userProfile");
  return profile ? JSON.parse(profile) : null;
}

export function setUserProfile(profile: any) {
  localStorage.setItem("userProfile", JSON.stringify(profile));
}

export function clearUserProfile() {
  localStorage.removeItem("userProfile");
}
