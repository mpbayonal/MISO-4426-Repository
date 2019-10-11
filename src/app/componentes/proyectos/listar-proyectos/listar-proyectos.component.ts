import { Component, OnInit } from '@angular/core';
import { ProyectoService } from 'src/app/servicios/proyecto/proyecto.service';
import { PageEvent } from '@angular/material/paginator';
import { UsuarioService } from 'src/app/servicios/usuario/usuario.service';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { FlashMessagesService } from 'angular2-flash-messages';


@Component({
  selector: 'app-listar-proyectos',
  templateUrl: './listar-proyectos.component.html',
  styleUrls: ['./listar-proyectos.component.css']
})
export class ListarProyectosComponent implements OnInit {

  public isLogged = false;
  proyectos: any = [];
  constructor(
    private proyectosService: ProyectoService,
    private usuarioService: UsuarioService,
    private rutaActiva: ActivatedRoute,
    private flashMessagesService: FlashMessagesService,
    private router: Router
  ) { }

  pageSize = 10;
  pageNumber = 1;

  chequearLogin() {
    if (this.usuarioService.getToken()) {
      this.isLogged = true;
    } else {
      this.isLogged = false;
    }
  }
  ngOnInit() {
    this.chequearLogin();
    if (localStorage.getItem('url') != null) {
      this.proyectosService.getProyectos(localStorage.getItem('url')).subscribe(
        res => {
          this.proyectos = res;
        }, err => console.log(err)
      );
    } else {
      this.proyectosService.getProyectos(this.rutaActiva.snapshot.params.url).subscribe(
        res => {
          this.proyectos = res;
          console.log(this.proyectos);
        }, err => console.log(err)
      )

    }
  }
  handlePage(e: PageEvent) {
    this.pageSize = e.pageSize;
    this.pageNumber = e.pageIndex + 1;
  }
  formularioAgregar() {
    this.router.navigate(['empresa/' + localStorage.getItem('url') + '/proyectos/agregar']);
  }
  eliminarProyecto(id) {
    this.proyectosService.eliminarProyecto(id).subscribe(
      res => {
        this.flashMessagesService.show('proyecto eliminado exitosamente', { cssClass: 'alert-success', timeout: 6000 });
        location.reload()
        this.router.navigate(['empresa/' + localStorage.getItem('url') + '/proyectos/']);

      },
      err => console.log(err)
    )
  }
  formularioEditar(id) {
    this.router.navigate(['empresa/proyectos/' + id + '/editar']);
  }
  mostrarDisenos(id) {
    this.router.navigate(['empresa/proyectos/' + id + '/disenos']);
  }

}