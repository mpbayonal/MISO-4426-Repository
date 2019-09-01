import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {

  API_URI = 'http://localhost:8000';
  constructor(private http: HttpClient) { }

  loginUsuario(usuario){
    return this.http.post(`${this.API_URI}/auth/login/`, usuario );
  }

  signUpUsuario(usuario){
    return this.http.post(`${this.API_URI}/auth/signup`, usuario );
  }

  setToken(token): void {
    localStorage.setItem("accessToken", token);
  }
  getToken() {
    return localStorage.getItem("accessToken");
  }
  logoutUser() {
    localStorage.removeItem("accessToken");
  }
}
