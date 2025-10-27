CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(100) NOT NULL,
    nome_completo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS Produtos (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    preco REAL NOT NULL CHECK(preco > 0),
    quantidade INTEGER NOT NULL CHECK(quantidade >= 0)
);

CREATE TABLE IF NOT EXISTS Vendas (
    id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente_fk INTEGER NOT NULL,
    id_produto_fk INTEGER NOT NULL,
    quantidade_vendida INTEGER NOT NULL,
    valor_total REAL NOT NULL,
    data_venda DATETIME NOT NULL,
    FOREIGN KEY (id_cliente_fk) REFERENCES Clientes (id_cliente),
    FOREIGN KEY (id_produto_fk) REFERENCES Produtos (id_produto)
);

INSERT INTO Usuarios (nome_usuario, senha, nome_completo) 
VALUES ('gerente', '1234', 'Gerente do Pet Shop');

INSERT INTO Clientes (nome_completo, telefone, email) 
VALUES 
('Marcos Silva', '62 99999-1001', 'marcos.silva@email.com'),
('Juliana Alves', '62 98888-1002', 'juliana.a@email.com'),
('Ricardo Souza', '62 97777-1003', 'ricardo.souza@email.com');

INSERT INTO Produtos (nome, categoria, preco, quantidade) 
VALUES 
('Ração Premium Cães 15kg', 'Alimentação', 189.90, 20),
('Brinquedo Ossinho de Borracha', 'Brinquedos', 29.50, 50),
('Shampoo Antipulgas 500ml', 'Higiene', 65.00, 30),
('Ração Golden Gatos 3kg', 'Alimentação', 89.90, 4);

INSERT INTO Vendas (id_cliente_fk, id_produto_fk, quantidade_vendida, valor_total, data_venda) 
VALUES 
(1, 2, 1, 29.50, '2025-10-20 09:30:00');