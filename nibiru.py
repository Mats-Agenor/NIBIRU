#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulação N-corpos — Sistema Solar + Planeta fictício Nibiru
------------------------------------------------------------
- Inclui Sol e 8 planetas reais.
- Adiciona planeta 'Nibiru' com:
    período orbital = 3600 anos,
    pericentro = 0.6 UA,
    massa = 6 massas de Júpiter.
- Integração com REBOUND por 36 mil anos.
- Saídas: gráficos de a(t), e(t), i(t) e r(t)
  para planetas terrestres e gigantes.
"""

import rebound
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.unicode_minus": False
})

# ===============================
# CONFIGURAÇÕES INICIAIS
# ===============================
sim = rebound.Simulation()
sim.G = 4 * np.pi**2  # unidades: M☉, UA, anos

# Adiciona o Sol
sim.add(m=1.0)

# Adiciona os 8 planetas com dados simplificados (aprox.)
# [massa (M☉), a (UA), e, inc (rad)]
planetas = [
    ("Mercúrio", 1.6601e-7, 0.387, 0.2056, 0.0),
    ("Vênus",    2.447e-6, 0.723, 0.0068, 0.0),
    ("Terra",    3.003e-6, 1.000, 0.0167, 0.0),
    ("Marte",    3.213e-7, 1.524, 0.0934, 0.0),
    ("Júpiter",  9.5458e-4, 5.203, 0.0489, 0.0),
    ("Saturno",  2.858e-4, 9.537, 0.0565, 0.0),
    ("Urano",    4.365e-5, 19.191, 0.0472, 0.0),
    ("Netuno",   5.15e-5, 30.07,  0.0097, 0.0)
]

for nome, m, a, e, inc in planetas:
    sim.add(m=m, a=a, e=e, inc=inc)

# ===============================
# ADICIONA NIBIRU
# ===============================
P = 3600.0  # período orbital (anos)
a_nib = P**(2/3)  # relação de Kepler (a³ = P²)
q_nib = 0.6  # pericentro (UA)
e_nib = 1.0 - q_nib/a_nib  # e = 1 - q/a
m_nib = 6.0 * 9.5458e-4  # 6 massas de Júpiter

print(f"Parâmetros de Nibiru:")
print(f"  Período: {P:.0f} anos")
print(f"  Semi-eixo maior a = {a_nib:.3f} UA")
print(f"  Excentricidade e = {e_nib:.6f}\n")

sim.add(m=m_nib, a=a_nib, e=e_nib, inc=0.0)

# Centraliza no centro de massa
sim.move_to_com()

# Configura integrador
sim.integrator = "ias15"  # integrador de alta precisão

# ===============================
# PARÂMETROS DE SIMULAÇÃO
# ===============================
Tmax = 36000.0  # anos
Noutputs = 1000
times = np.linspace(0, Tmax, Noutputs)

N = len(sim.particles)
nomes = ["Sol"] + [p[0] for p in planetas] + ["Nibiru"]

# Arrays para armazenar resultados
data = {i: {"a": [], "e": [], "inc": [], "r": []} for i in range(1, N)}  # ignora o Sol

# ===============================
# INTEGRAÇÃO PRINCIPAL
# ===============================
print(f"Iniciando simulação por {Tmax:.0f} anos com {Noutputs} saídas...\n")

for t in times:
    sim.integrate(t)
    orbits = sim.orbits()
    for i, orb in enumerate(orbits):  # ignora o Sol
        idx = i + 1
        data[idx]["a"].append(orb.a)
        data[idx]["e"].append(orb.e)
        data[idx]["inc"].append(np.degrees(orb.inc))
        data[idx]["r"].append(np.linalg.norm(sim.particles[idx].xyz))

print("Simulação concluída.\nGerando gráficos...")

# ===============================
# GRÁFICOS
# ===============================

# Índices: 1–4 = terrestres, 5–8 = gigantes, 9 = Nibiru
terrestres = [1, 2, 3, 4]
gigantes = [5, 6, 7, 8, 9]

def plot_group(indices, label):
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    axs = axs.flatten()
    for idx in indices:
        name = nomes[idx]
        axs[0].plot(times, data[idx]["a"], label=name)
        axs[1].plot(times, data[idx]["e"], label=name)
        axs[2].plot(times, data[idx]["inc"], label=name)
        axs[3].plot(times, data[idx]["r"], label=name)

    axs[0].set_ylabel("$a$ [UA]", fontsize=20)
    axs[1].set_ylabel("$e$", fontsize=20)
    axs[2].set_ylabel("$i$ [$^\\circ$]", fontsize=20)
    axs[3].set_ylabel("$r$ [UA]", fontsize=20)

    axs[0].set_title("Semi-eixo maior", fontsize=25)
    axs[1].set_title("Excentricidade", fontsize=25)
    axs[2].set_title("Inclinação", fontsize=25)
    axs[3].set_title("Distância ao Sol", fontsize=25)

    for ax in axs:

        ax.legend(fontsize=20)

    plt.suptitle(f"Planetas {label}", fontsize=30)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f"orbitas_{label.lower()}.png", dpi=150)
    plt.show()

plot_group(terrestres, "terrestres")
plot_group(gigantes, "gigantes")

print("Gráficos salvos.png")

