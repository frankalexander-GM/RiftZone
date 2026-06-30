package riftzone.dao;

import riftzone.connection.APIClient;
import riftzone.model.Transaccion;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;

public class TransaccionDAO {

    private Transaccion fromJson(JSONObject o) {
        Transaccion t = new Transaccion();
        t.setId(o.optInt("id"));
        t.setUserId(o.optInt("user_id"));
        t.setAmount(o.optInt("amount"));
        t.setTipo(o.optString("tipo", ""));
        t.setDescription(o.optString("description", ""));
        t.setCreatedAt(o.optString("created_at", null));
        return t;
    }

    private List<Transaccion> listarDesdeUrl(String url) throws Exception {
        List<Transaccion> lista = new ArrayList<>();
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

    public List<Transaccion> listar() throws Exception {
        return listarDesdeUrl("/api/transacciones");
    }

    public List<Transaccion> listarPorUsuario(int userId) throws Exception {
        if (userId <= 0) return listar();
        return listarDesdeUrl("/api/transacciones?user_id=" + userId);
    }

    public void insertar(Transaccion t) throws Exception {
        JSONObject o = new JSONObject();
        o.put("user_id", t.getUserId());
        o.put("amount", t.getAmount());
        o.put("tipo", t.getTipo());
        o.put("description", t.getDescription());
        APIClient.post("/api/transacciones", o.toString());
    }
}
