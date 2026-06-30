package riftzone.controller;

import riftzone.dao.UsuarioDAO;
import riftzone.model.Usuario;
import java.util.List;

public class UsuarioController {
    private UsuarioDAO dao = new UsuarioDAO();

    public List<Usuario> listar() throws Exception {
        return dao.listar();
    }

    public Usuario obtener(int id) throws Exception {
        return dao.obtener(id);
    }

    public String crear(String nombre, String username, String email, String password, String rol, String pais) {
        try {
            if (dao.obtenerPorEmail(email) != null) return "El email ya existe";
            Usuario u = new Usuario();
            u.setNombre(nombre); u.setUsername(username); u.setEmail(email);
            u.setPassword(password); u.setRol(rol); u.setPais(pais);
            u.setNivel(1); u.setTokens(0);
            dao.insertar(u);
            return null;
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    public String actualizar(int id, String nombre, String biografia, int nivel, int tokens, String pais, String rol) {
        try {
            Usuario u = dao.obtener(id);
            if (u == null) return "Usuario no encontrado";
            u.setNombre(nombre); u.setBiografia(biografia); u.setNivel(nivel);
            u.setTokens(tokens); u.setPais(pais); u.setRol(rol);
            dao.actualizar(u);
            return null;
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    public String eliminar(int id) {
        try {
            dao.eliminar(id);
            return null;
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }
}
