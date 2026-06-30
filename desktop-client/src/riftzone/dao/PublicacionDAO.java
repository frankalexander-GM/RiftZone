package riftzone.dao;

import riftzone.connection.APIClient;
import riftzone.model.Publicacion;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class PublicacionDAO {

    private Publicacion fromJson(JSONObject o) {
        Publicacion p = new Publicacion();
        p.setIdPublicacion(o.optInt("id_publicacion"));
        p.setIdUsuario(o.optInt("id_usuario"));
        p.setContenido(o.optString("contenido", ""));
        p.setImagenUrl(o.optString("imagen_url", null));
        p.setVideoArchivo(o.optString("video_archivo", null));
        p.setJuego(o.optString("juego", ""));
        p.setFechaCreacion(o.optString("fecha_creacion", null));
        p.setPromocionada(o.optBoolean("promocionada", false));
        p.setFijada(o.optBoolean("fijada", false));
        p.setSharesCount(o.optInt("shares_count", 0));
        p.setBoostTipo(o.optString("boost_tipo", null));
        p.setBoostHasta(o.optString("boost_hasta", null));
        return p;
    }

    private List<Publicacion> listarDesdeUrl(String url) throws Exception {
        List<Publicacion> lista = new ArrayList<>();
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

    public List<Publicacion> listar() throws Exception {
        return listarDesdeUrl("/api/publicaciones");
    }

    public List<Publicacion> listar(String juego) throws Exception {
        if (juego == null || juego.isEmpty()) return listar();
        return listarDesdeUrl("/api/publicaciones?juego=" + java.net.URLEncoder.encode(juego, "UTF-8"));
    }

    public List<Publicacion> listarPorUsuario(int idUsuario) throws Exception {
        return listarDesdeUrl("/api/publicaciones?id_usuario=" + idUsuario);
    }

    public Publicacion obtener(int id) throws Exception {
        String json = APIClient.get("/api/publicaciones/" + id);
        JSONObject o = new JSONObject(json);
        if (o.has("error")) return null;
        return fromJson(o);
    }

    public void insertar(Publicacion p) throws Exception {
        JSONObject o = new JSONObject();
        o.put("id_usuario", p.getIdUsuario());
        o.put("contenido", p.getContenido());
        o.put("juego", p.getJuego());
        if (p.getImagenUrl() != null) o.put("imagen_url", p.getImagenUrl());
        if (p.getVideoArchivo() != null) o.put("video_archivo", p.getVideoArchivo());
        APIClient.post("/api/publicaciones", o.toString());
    }

    public void actualizar(Publicacion p) throws Exception {
        JSONObject o = new JSONObject();
        o.put("contenido", p.getContenido());
        o.put("juego", p.getJuego());
        if (p.getImagenUrl() != null) o.put("imagen_url", p.getImagenUrl());
        if (p.getVideoArchivo() != null) o.put("video_archivo", p.getVideoArchivo());
        o.put("promocionada", p.isPromocionada());
        APIClient.put("/api/publicaciones/" + p.getIdPublicacion(), o.toString());
    }

    public void eliminar(int id) throws Exception {
        APIClient.delete("/api/publicaciones/" + id);
    }
}
