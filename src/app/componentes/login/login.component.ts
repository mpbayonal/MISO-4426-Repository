import { Component, OnInit } from '@angular/core';
import { UsuarioService } from 'src/app/servicios/usuario/usuario.service';
import { Router } from '@angular/router';
import { Location } from '@angular/common';
import { FlashMessagesService } from 'angular2-flash-messages';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {


  constructor(
    private usuarioService: UsuarioService,
    private router: Router, private location: Location,
    private flashMessagesService: FlashMessagesService
  ) { }

  usuario = {
    username: '',
    email: '',
    password: ''
  };
  credenciales: any = {};

  setUsuario() {
    localStorage.setItem('usuario', this.usuario.username);
  }
  getUsuario() {
    return localStorage.getItem('usuario');
  }
  login() {
    this.usuarioService.getUrl(this.usuario.email).subscribe(
      data2 => {
        this.credenciales = data2;
        localStorage.setItem('url', this.credenciales.url);
        localStorage.setItem('id', this.credenciales.id);
        localStorage.setItem('email', this.credenciales.email);
      }
    )
    this.usuarioService.loginUsuario(this.usuario).subscribe(
      data => {

        const token = data;
        this.usuarioService.setToken(token);
        this.setUsuario();
        this.router.navigate(['empresa/' + localStorage.getItem('url') + '/proyectos']);
        location.reload();
        this.flashMessagesService.show('Inició Sesión exitosamente', { cssClass: 'alert-success', timeout: 6000 });
      }, err => {
        this.flashMessagesService.show('Contraseña, email o username incorrecto', { cssClass: 'alert-danger', timeout: 6000 });
      }
    );
  }



  ngOnInit() {

  }

}