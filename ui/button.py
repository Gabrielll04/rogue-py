class Button:
    def __init__(
        self,
        texto,
        x,
        y,
        largura=200,
        altura=60,
        cor="white",
        cor_hover="yellow",
    ):
        self.text = texto
        self.x = x
        self.y = y
        self.width = largura
        self.heigth = altura
        self.color = cor
        self.color_hover = cor_hover
        self.hover = False

    def draw(self, screen):
        from pgzero.rect import Rect

        actual_color = self.color_hover if self.hover else self.color
        rect = Rect((self.x, self.y), (self.width, self.heigth))
        screen.draw.filled_rect(rect, actual_color)
        screen.draw.text(
            self.text,
            center=(self.x + self.width / 2, self.y + self.heigth / 2),
            fontsize=40,
            color="black",
        )

    def verify_hover(self, pos):
        self.hover = (
            self.x <= pos[0] <= self.x + self.width
            and self.y <= pos[1] <= self.y + self.heigth
        )

    def clicked(self, pos):
        return (
            self.x <= pos[0] <= self.x + self.width
            and self.y <= pos[1] <= self.y + self.heigth
        )
