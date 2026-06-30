package riftzone.dao;

import riftzone.connection.APIClient;
import riftzone.model.MensajeChat;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class MensajeChatDAO {

    private MensajeChat fromJson(JSONObject o) {
        MensajeChat m = new MensajeChat();
        m.setId(o.optInt("id"));
        m.setUsuarioId(o.optInt("usuario_id"));
        m.setContenido(o.optString("contenido", ""));
        m.setFechaEnvio(o.optString("fecha_envio", null));
        return m;
    }

    public List<MensajeChat> listar() throws Exception {
        List<MensajeChat> lista = new ArrayList<>();
        String json = APIClient.get("/api/chat");
        JSONObject page = new JSONObject(json);
        JSONArray arr = page.optJSONArray("data");
        if (arr != null) {
            for (int i = 0; i < arr.length(); i++) {
                lista.add(fromJson(arr.getJSONObject(i)));
            }
        }
        return lista;
    }

    public void insertar(MensajeChat m) throws Exception {
        JSONObject o = new JSONObject();
        o.put("contenido", m.getContenido());
        APIClient.post("/api/chat", o.toString());
    }

    public void eliminar(int id) throws Exception {
        APIClient.delete("/api/chat/" + id);
    }
}
