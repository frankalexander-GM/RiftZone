package riftzone.dao;

import riftzone.connection.APIClient;
import riftzone.model.Comentario;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class ComentarioDAO {

    private Comentario fromJson(JSONObject o) {
        Comentario c = new Comentario();
        c.setIdComentario(o.optInt("id_comentario"));
        c.setIdPublicacion(o.optInt("id_publicacion"));
        c.setIdUsuario(o.optInt("id_usuario"));
        c.setContenido(o.optString("contenido", ""));
        c.setFechaCreacion(o.optString("fecha_creacion", null));
        return c;
    }

    private List<Comentario> listarDesdeUrl(String url) throws Exception {
        List<Comentario> lista = new ArrayList<>();
        String json = APIClient.get(url);
        JSONObject page = new JSONObject(json);
        JSONArray arr = page.optJSONArray("data");
        if (arr != null) {
            for (int i = 0; i < arr.length(); i++) {
                lista.add(fromJson(arr.getJSONObject(i)));
            }
        }
        return lista;
    }

    public List<Comentario> listar() throws Exception {
        return listarDesdeUrl("/api/comentarios");
    }

    public List<Comentario> listarPorPublicacion(int idPublicacion) throws Exception {
        if (idPublicacion <= 0) return listar();
        return listarDesdeUrl("/api/comentarios?id_publicacion=" + idPublicacion);
    }

    public Comentario obtener(int id) throws Exception {
        String json = APIClient.get("/api/comentarios/" + id);
        JSONObject o = new JSONObject(json);
        if (o.has("error")) return null;
        return fromJson(o);
    }

    public void insertar(Comentario c) throws Exception {
        JSONObject o = new JSONObject();
        o.put("id_publicacion", c.getIdPublicacion());
        o.put("id_usuario", c.getIdUsuario());
        o.put("contenido", c.getContenido());
        APIClient.post("/api/comentarios", o.toString());
    }

    public void eliminar(int id) throws Exception {
        APIClient.delete("/api/comentarios/" + id);
    }
}
