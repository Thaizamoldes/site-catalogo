# Catálogo de Moldes

Site estático e leve com os modelos da assinatura de moldes, separados por categoria.

- `docs/` – o site publicado (HTML único, sem bibliotecas externas, fotos em WebP com carregamento sob demanda).
- `fotos/<Categoria>/<Nome do modelo>.jpg` – fotos originais, organizadas por categoria.
- `build.py` – gera as imagens otimizadas e a lista de modelos a partir de `fotos/`.

## Adicionar ou renomear modelos

1. Coloque a foto em `fotos/<Categoria>/` com o nome do modelo como nome do arquivo
   (para uma categoria nova, basta criar a pasta).
2. Rode:
   ```
   pip install pillow pillow-heif
   python3 build.py
   ```
3. Faça commit das mudanças em `fotos/` e `docs/`.

## Publicar (GitHub Pages)

Em **Settings → Pages**, escolha *Deploy from a branch*, a branch desejada e a pasta `/docs`.
