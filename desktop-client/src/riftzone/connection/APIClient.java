package riftzone.connection;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class APIClient {
    public static String BASE_URL = "https://ritfzone.online";
    private static String token;

    public static void setToken(String t) { token = t; }
    public static String getToken() { return token; }

    public static String get(String endpoint) throws IOException {
        return request("GET", endpoint, null);
    }

    public static String post(String endpoint, String jsonBody) throws IOException {
        return request("POST", endpoint, jsonBody);
    }

    public static String put(String endpoint, String jsonBody) throws IOException {
        return request("PUT", endpoint, jsonBody);
    }

    public static String delete(String endpoint) throws IOException {
        return request("DELETE", endpoint, null);
    }

    private static String request(String method, String endpoint, String jsonBody) throws IOException {
        URL url = new URL(BASE_URL + endpoint);
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod(method);
        con.setRequestProperty("Content-Type", "application/json");
        con.setRequestProperty("Accept", "application/json");
        con.setConnectTimeout(15000);
        con.setReadTimeout(15000);
        if (token != null && !token.isEmpty()) {
            con.setRequestProperty("Authorization", "Bearer " + token);
        }
        if (jsonBody != null && !jsonBody.isEmpty()) {
            con.setDoOutput(true);
            try (OutputStream os = con.getOutputStream()) {
                os.write(jsonBody.getBytes(StandardCharsets.UTF_8));
            }
        }
        int status = con.getResponseCode();
        InputStream stream = (status >= 200 && status < 300) ? con.getInputStream() : con.getErrorStream();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) sb.append(line);
            return sb.toString();
        }
    }
}
