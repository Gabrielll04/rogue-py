class Botao:
    def __init__(self, texto, x, y, largura=200, altura=60, cor="white", cor_hover="yellow"):
        self.texto = texto
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.cor = cor
        self.cor_hover = cor_hover
        self.hover = False

    def desenhar(self, screen):
        from pgzero.rect import Rect  # importa aqui pra evitar conflitos
        cor_atual = self.cor_hover if self.hover else self.cor
        rect = Rect((self.x, self.y), (self.largura, self.altura))
        screen.draw.filled_rect(rect, cor_atual)
        screen.draw.text(
            self.texto,
            center=(self.x + self.largura/2, self.y + self.altura/2),
            fontsize=40,
            color="black"
        )

    def verificar_hover(self, pos):
        self.hover = (self.x <= pos[0] <= self.x + self.largura and
                      self.y <= pos[1] <= self.y + self.altura)

    def clicado(self, pos):
        return (self.x <= pos[0] <= self.x + self.largura and
                self.y <= pos[1] <= self.y + self.altura)