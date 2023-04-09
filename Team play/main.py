import settings as set
import pygame
import game

pygame.init()

pygame.mixer.Channel(0).play(pygame.mixer.Sound('assets\Menu\menu.mp3'))

BackGroundImage = pygame.image.load("assets\Menu\Background.png")
BackGroundImage = pygame.transform.scale(BackGroundImage, (set.WIDTH, set.HEIGHT))

pygame.display.set_caption("Platformer")
window = pygame.display.set_mode((set.WIDTH, set.HEIGHT))

class Button():
     def __init__(self, image, pos, text_input, font, base_color, hovering_color):
         self.image = image
         self.x_pos = pos[0]
         self.y_pos = pos[1]
         self.font = font
         self.base_color, self.hovering_color = base_color, hovering_color
         self.text_input = text_input
         self.text = self.font.render(self.text_input, True, self.base_color)
         if self.image is None:
             self.image = self.text
         self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
         self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

     def update(self, screen):
         if self.image is not None:
             screen.blit(self.image, self.rect)
         screen.blit(self.text, self.text_rect)

     def checkForInput(self, position):
         if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                           self.rect.bottom):
             return True
         return False

     def changeColor(self, position):
         if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                           self.rect.bottom):
             self.text = self.font.render(self.text_input, True, self.hovering_color)
         else:
             self.text = self.font.render(self.text_input, True, self.base_color)

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/Menu/font.ttf", size)

def levels_menu():

    window.blit(BackGroundImage, (0, 0))

    levels_pos = {}

    for i in range(1, set.LEVELS + 1):
        x = 10 + ((i - 1) % 3 + 1) * 260
        y = 160 + ((i - 1) // 3) * 200
        levels_pos[f'{x}:{y}'] = i

    levels = []

    for i in range(1, set.LEVELS + 1):
        x = 10 + ((i - 1) % 3 + 1) * 260
        y = 160 + ((i - 1) // 3) * 200

        lev_image = pygame.image.load(f"assets/Menu/Levels/{i}_off.png" if i > set.CURRENT_MAX_LEVEL else f"assets/Menu/Levels/{i}.png")
        lev_image = pygame.transform.scale(lev_image, (100, 100))

        level= Button(image=lev_image, pos=(x, y), text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        level.update(window)
        levels.append(level)

    while True:

        MOUSE_POS = pygame.mouse.get_pos()

        OPTIONS_BACK = Button(image=None, pos=(520, 725), text_input="BACK", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BACK.changeColor(MOUSE_POS)
        OPTIONS_BACK.update(window)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(MOUSE_POS):
                    main_menu()
                for level in levels:
                    if level.checkForInput(MOUSE_POS):
                        if levels_pos[f'{level.x_pos}:{level.y_pos}'] <= set.CURRENT_MAX_LEVEL:
                            set.CURRENT_LEVEL = levels_pos[f'{level.x_pos}:{level.y_pos}']
                            pygame.mixer.Channel(0).pause()
                            game.CURRENT_LEVEL = levels_pos[f'{level.x_pos}:{level.y_pos}']
                            game.play()
                        else:
                            pygame.mixer.Channel(1).play(pygame.mixer.Sound('assets\Music\8 bit uh oh sound.mp3'))


        pygame.display.update()

def main_menu():

    pygame.mixer.Channel(0).unpause() # in case we return from game

    window.blit(BackGroundImage, (0, 0))

    play_button = Button(image=None, pos=(520, 300), text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
    quit_button = Button(image=None, pos=(520, 470), text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

    while True:

        mouse_pos = pygame.mouse.get_pos()

        for button in [play_button, quit_button]:
            button.changeColor(mouse_pos)
            button.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(mouse_pos):
                    levels_menu()
                if quit_button.checkForInput(mouse_pos):
                    pygame.quit()

        pygame.display.update()

def main():
    main_menu()

if __name__ == "__main__":
    main()