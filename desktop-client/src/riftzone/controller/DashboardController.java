package riftzone.controller;

import riftzone.connection.APIClient;
import org.json.JSONObject;
import java.util.LinkedHashMap;
import java.util.Map;

public class DashboardController {

    public Map<String, Object> getEstadisticas() {
        Map<String, Object> stats = new LinkedHashMap<>();
        try {
            String json = APIClient.get("/api/estadisticas");
            JSONObject o = new JSONObject(json);
            for (String key : o.keySet()) {
                stats.put(key, o.get(key));
            }
        } catch (Exception e) {
            stats.put("error", e.getMessage());
        }
        return stats;
    }
}
