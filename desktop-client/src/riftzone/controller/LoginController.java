package riftzone.controller;

import riftzone.connection.APIClient;
import riftzone.model.Usuario;
import org.json.JSONObject;

public class LoginController {

    public Usuario login(String email, String password) {
        if (email == null || email.trim().isEmpty() || password == null || password.trim().isEmpty()) {
            return null;
        }
        try {
            JSONObject body = new JSONObject();
            body.put("email", email.trim().toLowerCase());
            body.put("password", password);
            String json = APIClient.post("/api/login", body.toString());
            JSONObject resp = new JSONObject(json);
            if (resp.optBoolean("success", false)) {
                APIClient.setToken(resp.optString("token", ""));
                JSONObject userJson = resp.optJSONObject("user");
                if (userJson != null) {
                    Usuario u = new Usuario();
                    u.setIdUsuario(userJson.optInt("id_usuario"));
                    u.setNombre(userJson.optString("nombre", ""));
                    u.setUsername(userJson.optString("username", ""));
                    u.setEmail(userJson.optString("email", ""));
                    u.setRol(userJson.optString("rol", "jugador"));
                    u.setNivel(userJson.optInt("nivel", 1));
                    u.setTokens(userJson.optInt("tokens", 0));
                    u.setPais(userJson.optString("pais", null));
                    return u;
                }
            }
        } catch (Exception e) {
            System.err.println("[LoginController] Error en login: " + e.getClass().getName() + ": " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Error de conexion: " + e.getMessage(), e);
        }
        return null;
    }
}
