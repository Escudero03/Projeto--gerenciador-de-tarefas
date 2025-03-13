import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
from datetime import datetime

class Tarefa:
    def __init__(self, titulo, categoria, data_vencimento, concluida=False):
        self.titulo = titulo
        self.categoria = categoria
        self.data_vencimento = data_vencimento
        self.concluida = concluida

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "categoria": self.categoria,
            "data_vencimento": self.data_vencimento,
            "concluida": self.concluida,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["titulo"],
            data["categoria"],
            data["data_vencimento"],
            data["concluida"],
        )

class GerenciadorTarefas:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas")

        self.tarefas = self.carregar_tarefas()

        self.criar_interface()
        self.atualizar_lista_tarefas()

    def carregar_tarefas(self):
        try:
            with open("tarefas.json", "r") as f:
                data = json.load(f)
            return [Tarefa.from_dict(t) for t in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_tarefas(self):
        try:
            with open("tarefas.json", "w") as f:
                json.dump([t.to_dict() for t in self.tarefas], f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar tarefas: {e}")

    def criar_interface(self):
        frame_lista = ttk.Frame(self.root)
        frame_lista.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.lista_tarefas = ttk.Treeview(
            frame_lista, columns=("Titulo", "Categoria", "Data", "Concluida"), show="headings"
        )
        self.lista_tarefas.heading("Titulo", text="Título")
        self.lista_tarefas.heading("Categoria", text="Categoria")
        self.lista_tarefas.heading("Data", text="Data")
        self.lista_tarefas.heading("Concluida", text="Concluída")
        self.lista_tarefas.pack(fill=tk.BOTH, expand=True)

        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack(pady=5)

        ttk.Button(frame_botoes, text="Adicionar", command=self.adicionar_tarefa).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Editar", command=self.editar_tarefa).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Concluir/Desfazer", command=self.concluir_tarefa).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", command=self.excluir_tarefa).pack(side=tk.LEFT, padx=5)

    def adicionar_tarefa(self):
        titulo = simpledialog.askstring("Adicionar Tarefa", "Título:")
        if not titulo:
            return
        categoria = simpledialog.askstring("Adicionar Tarefa", "Categoria:") or "Sem categoria"
        data_str = simpledialog.askstring("Adicionar Tarefa", "Data (AAAA-MM-DD):")
        try:
            data_vencimento = datetime.strptime(data_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messagebox.showerror("Erro", "Formato de data inválido (AAAA-MM-DD).")
            return
        concluida = simpledialog.askinteger("Adicionar Tarefa", "Concluída (0: Não, 1: Sim):", minvalue=0, maxvalue=1)
        if concluida is None:
            return
        tarefa = Tarefa(titulo, categoria, data_vencimento.strftime("%Y-%m-%d"), bool(concluida))
        self.tarefas.append(tarefa)
        self.salvar_tarefas()
        self.atualizar_lista_tarefas()

    def editar_tarefa(self):
        item_selecionado = self.lista_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para editar.")
            return
        if len(item_selecionado) > 1:
            messagebox.showwarning("Aviso", "Selecione apenas uma tarefa para editar.")
            return

        try:
            indice = int(item_selecionado[0])  # O IID é o índice na lista
            print(f"Editando - Índice: {indice}, Tamanho da lista: {len(self.tarefas)}")  # Depuração
            if 0 <= indice < len(self.tarefas):
                tarefa = self.tarefas[indice]
                titulo = simpledialog.askstring("Editar Tarefa", "Título:", initialvalue=tarefa.titulo)
                if not titulo:
                    return
                categoria = simpledialog.askstring("Editar Tarefa", "Categoria:", initialvalue=tarefa.categoria) or "Sem categoria"
                data_str = simpledialog.askstring("Editar Tarefa", "Data (AAAA-MM-DD):", initialvalue=tarefa.data_vencimento)
                try:
                    data_vencimento = datetime.strptime(data_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    messagebox.showerror("Erro", "Formato de data inválido (AAAA-MM-DD).")
                    return
                concluida = simpledialog.askinteger("Editar Tarefa", "Concluída (0: Não, 1: Sim):", initialvalue=int(tarefa.concluida), minvalue=0, maxvalue=1)
                if concluida is None:
                    return

                tarefa.titulo = titulo
                tarefa.categoria = categoria
                tarefa.data_vencimento = data_vencimento.strftime("%Y-%m-%d")
                tarefa.concluida = bool(concluida)

                self.salvar_tarefas()
                self.atualizar_lista_tarefas()
            else:
                messagebox.showerror("Erro", f"Índice inválido: {indice} fora do intervalo (0-{len(self.tarefas)-1})")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao processar índice: {e}")

    def concluir_tarefa(self):
        item_selecionado = self.lista_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir/desfazer.")
            return

        try:
            indice = int(item_selecionado[0])
            print(f"Concluindo - Índice: {indice}, Tamanho da lista: {len(self.tarefas)}")  # Depuração
            if 0 <= indice < len(self.tarefas):
                tarefa = self.tarefas[indice]
                tarefa.concluida = not tarefa.concluida
                self.salvar_tarefas()
                self.atualizar_lista_tarefas()
            else:
                messagebox.showerror("Erro", f"Índice inválido: {indice}")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao processar índice: {e}")

    def excluir_tarefa(self):
        item_selecionado = self.lista_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para excluir.")
            return

        try:
            indice = int(item_selecionado[0])
            print(f"Excluindo - Índice: {indice}, Tamanho da lista: {len(self.tarefas)}")  # Depuração
            if 0 <= indice < len(self.tarefas):
                del self.tarefas[indice]
                self.salvar_tarefas()
                self.atualizar_lista_tarefas()
            else:
                messagebox.showerror("Erro", f"Índice inválido: {indice} fora do intervalo (0-{len(self.tarefas)-1})")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao processar índice: {e}")

    def atualizar_lista_tarefas(self):
        for item in self.lista_tarefas.get_children():
            self.lista_tarefas.delete(item)
        for i, tarefa in enumerate(self.tarefas):
            self.lista_tarefas.insert(
                "", tk.END, iid=str(i),
                values=(tarefa.titulo, tarefa.categoria, tarefa.data_vencimento, "Sim" if tarefa.concluida else "Não")
            )
        print(f"Lista atualizada - Tamanho: {len(self.tarefas)}")  # Depuração

if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorTarefas(root)
    root.mainloop()