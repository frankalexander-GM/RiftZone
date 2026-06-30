package riftzone.dao;

import riftzone.connection.APIClient;
import riftzone.model.Usuario;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class UsuarioDAO {

    private Usuario fromJson(JSONObject o) {
        Usuario u = new Usuario();
        u.setIdUsuario(o.optInt("id_usuario"));
        u.setNombre(o.optString("nombre", ""));
        u.setUsername(o.optString("username", ""));
        u.setEmail(o.optString("email", ""));
        u.setPassword(o.optString("password", ""));
        u.setRol(o.optString("rol", "jugador"));
        u.setBiografia(o.optString("biografia", null));
        u.setNivel(o.optInt("nivel", 1));
        u.setXp(o.optInt("xp", 0));
        u.setTokens(o.optInt("tokens", 0));
        u.setPais(o.optString("pais", null));
        u.setFechaRegistro(o.optString("fecha_registro", null));
        return u;
    }

    public List<Usuario> listar() throws Exception {
        List<Usuario> lista = new ArrayList<>();
        String json = APIClient.get("/api/usuarios");
        JSONObject page = new JSONObject(json);
        JSONArray arr = page.optJSONArray("data");
        if (arr != null) {
            for (int i = 0; i < arr.length(); i++) {
                lista.add(fromJson(arr.getJSONObject(i)));
            }
        }
        return lista;
    }

    public Usuario obtener(int id) throws Exception {
        String json = APIClient.get("/api/usuarios/" + id);
        JSONObject o = new JSONObject(json);
        if (o.has("error")) return null;
        return fromJson(o);
    }

    public Usuario obtenerPorEmail(String email) throws Exception {
        List<Usuario> todos = listar();
        for (Usuario u : todos) {
            if (email.equalsIgnoreCase(u.getEmail())) return u;
        }
        return null;
    }

    public void insertar(Usuario u) throws Exception {
        JSONObject o = new JSONObject();
        o.put("nombre", u.getNombre()); o.put("username", u.getUsername());
        o.put("email", u.getEmail()); o.put("password", u.getPassword());
        o.put("rol", u.getRol() != null ? u.getRol() : "jugador");
        o.put("pais", u.getPais() != null ? u.getPais() : "");
        o.put("tokens", u.getTokens());
        APIClient.post("/api/usuarios", o.toString());
    }

    public void actualizar(Usuario u) throws Exception {
        JSONObject o = new JSONObject();
        o.put("nombre", u.getNombre()); o.put("biografia", u.getBiografia());
        o.put("nivel", u.getNivel()); o.put("tokens", u.getTokens());
        o.put("pais", u.getPais()); o.put("rol", u.getRol());
        APIClient.put("/api/usuarios/" + u.getIdUsuario(), o.toString());
    }

    public void eliminar(int id) throws Exception {
        APIClient.delete("/api/usuarios/" + id);
    }
}
