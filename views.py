from app import app, db, login_manager
from flask import render_template, url_for, redirect, request, flash
import requests
from models import Playlist, User
from flask_login import login_user, logout_user, current_user

lingua = 'pt-BR'
regiao = 'BR'

apiurl = 'https://api.themoviedb.org/3/'
chave = '?api_key=8ef9c4bb105f7ff666257615fa6d4f97'
filmes = []

#  --->  Usuario  <---  #


@app.route('/User/Cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('vermelho')
            flash('Usuário já existe!')
            return redirect(url_for('cadastro'))
        user = User.query.filter_by(username=username).first()
        if user:
            flash('vermelho')
            flash('Usuário já existe!')
            return redirect(url_for('cadastro'))
        
        user = User(username, email, password)
        
        db.session.add(user)
        db.session.commit()
        flash('green')
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
        
    return render_template('user/cadastro.html')




@app.route('/User/Login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            flash('vermelho')
            flash('Verifique a senha e email')
            return redirect(url_for('login'))
        flash('green')
        flash('login feito com sucesso')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('user/login.html')


@app.route('/Logout')
def logout():
    flash('green')
    flash('Logout feito com sucesso!')
    logout_user()
    return redirect(url_for('login'))

#  --->  Filmes  <---  #

def boleano(string):
    if string == 'True':
        return True
    else: 
        return False

def check_filme(filme_local):
    playlists = Playlist.query.filter_by(usuario=current_user.id).all()
    for l in playlists:
        if (filme_local['title'] == l.titulo) or (filme_local['original_title'] == l.titulo):
            return True
    return False


@app.route('/')
@app.route('/Home')
def index():
    url = f'https://api.themoviedb.org/3/movie/popular{chave}&language=en-US&page=1'
    valor = requests.get(url)
    list_filmes = valor.json()['results']
    
    return render_template('index.html', list_filmes=list_filmes)


@app.route('/Pesquisar', methods=['GET', 'POST'])
def pesquisar():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        filmes.clear()
        titulofilme = request.form['titulofilme']
        
        url = f'{apiurl}search/movie{chave}&language={lingua}&region={regiao}&query={titulofilme}'
        
        valor = requests.get(url)
        list_filmes = valor.json()['results']
    
        for filmee in list_filmes:
            if check_filme(filmee):
                continue
            else:
                filmes.append([filmee['original_title'], f'https://image.tmdb.org/t/p/w500{filmee["backdrop_path"]}', filmee['title']])
        return redirect(url_for('pesquisar'))
    return render_template('pesquisar.html', filmes=filmes)


@app.route('/Playlist/Adicionar', methods=['GET', 'POST'])
def adicionar():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    title = request.args.get('title')
    img = request.args.get('img')
    if request.method == 'POST':
        title_recebido = request.form['title']
        status = boleano(request.form['status'])
        favorito = boleano(request.form['favorito'])
        avaliacao = request.form['avaliacao']
        
        
        playlist = Playlist(title_recebido, status, avaliacao, favorito, current_user.id)
        db.session.add(playlist)
        db.session.commit()
        filmes.clear()
        flash('green')
        flash('Filme adicionado a playlist com sucesso!')
        return redirect(url_for('pesquisar'))
    
    return render_template('addfilme.html', title=title, img=img)


@app.route('/Playlist', methods=['GET', 'POST'])
def meusfilmes():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    playlists = Playlist.query.filter_by(usuario=current_user.id)
    return render_template('dbfilmes.html', playlists=playlists)

@app.route('/Playlist/Editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    playlist = Playlist.query.filter_by(id=id).first()
    if request.method == 'POST':
        playlist.status = boleano(request.form['status'])
        playlist.favorito = boleano(request.form['favorito'])
        playlist.avaliacao = request.form['avaliacao']
        db.session.commit()
        flash('green')
        flash('Filme editado com sucesso!')
        return redirect(url_for('meusfilmes'))
    return render_template('editar.html', id=id, playlist=playlist)

@app.route('/Playlist/Deletar/<int:id>', methods=['GET', 'POST'])
def deletar(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    playlist = Playlist.query.filter_by(id=id).first()
    if request.method == 'POST':
        db.session.delete(playlist)
        db.session.commit()
        flash('green')
        flash('Filme deletado com sucesso!')
        return redirect(url_for('meusfilmes'))
    return render_template('excluir.html', playlist=playlist)
