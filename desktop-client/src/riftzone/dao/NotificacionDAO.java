package riftzone.dao;

import riftzone.connection.APIClient;
import riftzone.model.Notificacion;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class NotificacionDAO {

    private Notificacion fromJson(JSONObject o) {
        Notificacion n = new Notificacion();
        n.setIdNotificacion(o.optInt("id_notificacion"));
        n.setUsuarioId(o.optInt("usuario_id"));
        n.setMensaje(o.optString("mensaje", ""));
        n.setIcono(o.optString("icono", "fas fa-bell"));
        n.setEnlace(o.optString("enlace", null));
        n.setTipo(o.optString("tipo", "sistema"));
        n.setLeido(o.optBoolean("leido", false));
        n.setFechaCreacion(o.optString("fecha_creacion", null));
        return n;
    }

    private List<Notificacion> listarDesdeUrl(String url) throws Exception {
        List<Notificacion> lista = new ArrayList<>();
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

    public List<Notificacion> listar() throws Exception {
        return listarDesdeUrl("/api/notificaciones");
    }

    public List<Notificacion> listarPorUsuario(int usuarioId) throws Exception {
        if (usuarioId <= 0) return listar();
        return listarDesdeUrl("/api/notificaciones?usuario_id=" + usuarioId);
    }

    public void insertar(Notificacion n) throws Exception {
        JSONObject o = new JSONObject();
        o.put("usuario_id", n.getUsuarioId());
        o.put("mensaje", n.getMensaje());
        o.put("icono", n.getIcono() != null ? n.getIcono() : "fas fa-bell");
        o.put("enlace", n.getEnlace());
        o.put("tipo", n.getTipo() != null ? n.getTipo() : "sistema");
        APIClient.post("/api/notificaciones", o.toString());
    }

    public void marcarLeida(int id, boolean leido) throws Exception {
        JSONObject o = new JSONObject();
        o.put("leido", leido);
        APIClient.put("/api/notificaciones/" + id, o.toString());
    }

    public void eliminar(int id) throws Exception {
        APIClient.delete("/api/notificaciones/" + id);
    }
}
