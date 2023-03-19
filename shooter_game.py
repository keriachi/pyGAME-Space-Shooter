from pygame import *
from random import randint
from time import time
# подгружаем отдельно функции для работы со шрифтом
font.init()
font1 = font.Font('Arial', 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

font2 = font.Font(None, 36)
font3 = font.Font(None, 50)


#фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
# mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# нам нужны такие картинки:
img_back = "galaxy.jpg" # фон игры 
img_bullet = "bullet.png" # пуля
img_hero = "rocket.png" # герой
img_enemy = "ufo.png" # враг
img_meteor = "asteroid.png" # враг
 
score = 0 # сбито кораблей
goal = 10 # столько кораблей нужно сбить для победы
lost = 0 # пропущено кораблей
max_lost = 3 # проиграли, если пропустили столько
life = 3 # счетчик жизней
 
# класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
  # конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # Вызываем конструктор класса (Sprite):
        sprite.Sprite.__init__(self)

        # каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
 
  # метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# класс главного игрока
class Player(GameSprite):
    # метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
  # метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

# класс спрайта-врага   
class Enemy(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
        # исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1

# класс спрайта-врага   
class Meteor(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        # исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
 
# класс спрайта-пули   
class Bullet(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        # исчезает, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()
 
# Создаем окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
 
# создаем спрайты
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
 
bullets = sprite.Group()
 
# переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False
# Основной цикл игры:
run = True # флаг сбрасывается кнопкой закрытия окна

def setColor():
    text_color = (0, 0, 0)
    if life == 3:
        text_color = (0, 255, 0)
    elif life == 2:
        text_color = (0, 255, 255)
    elif life == 1:
        text_color = (255, 0, 0)
    return text_color

    

while run:
    # событие нажатия на кнопку Закрыть
    for e in event.get():
        if e.type == QUIT:
            run = False
        # событие нажатия на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and rel_time == False:
                    num_fire = num_fire + 1
                    fire_sound.play()
                    ship.fire()

                if num_fire >=5 and rel_time == False:
                    last_time = timer = timer()
                    rel_time = True
                
  # сама игра: действия спрайтов, проверка правил игры, перерисовка
    if not finish:
        # обновляем фон
        window.blit(background,(0,0))

        # производим движения спрайтов
        ship.update()
        monsters.update()
        meteors.update()
        bullets.update()

        # обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        monsters.draw(window)
        meteors.draw(window)
        bullets.draw(window)

        if rel_time == True:
            now_time = timer()

        if now_time - last_time < 3:
            reload = font2.render('Wait, reload...', 1, (150, 0, 0))
            window.blit(reload, (260, 460))
        else:
            num_fire = 0
            rel_time = False
 
        # проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            # этот цикл повторится столько раз, сколько монстров подбито
            score = score + 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # возможный проигрыш: пропустили слишком много или герой столкнулся с врагом
        if sprite.spritecollide(ship, monsters, True) or sprite.spritecollide(ship, meteors, True):
            life -= 1

        if lost >= max_lost or life == 0:
            finish = True # проиграли, ставим фон и больше не управляем спрайтами.
            window.blit(lose, (200, 200))

        # проверка выигрыша: сколько очков набрали?
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        # пишем текст на экране
        text = font2.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        text_color = setColor()
        text_life = font3.render(str(life), 1, (0, 255, 0))
        window.blit(text_life, (win_width-50, 10))

        display.update()
    else:
        finish = False
        score = 0
        lost = 0
        life = 3
        for m in monsters:
            m.kill()

        for b in monsters:
            b.kill()

        for mtr in monsters:
            mtr.kill()

        time.delay(3000)

        for i in range(1, 6):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
        for i in range(2):
            meteor = Meteor(img_meteor, randint(80, win_width - 80), -40, 50, 50, randint(5, 10))
            meteors.add(meteor)
    
    # цикл срабатывает каждую 0.05 секунд
            time.delay(50)