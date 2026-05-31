import numpy as np
import matplotlib.pyplot as plt

elasticity_values = [-0.1, -0.3, -0.5]
price_signal = np.linspace(0.8, 1.8, 100)

plt.figure(figsize=(8, 5))

for e in elasticity_values:
    price_effect = price_signal ** e
    plt.plot(price_signal, price_effect, label=f'Elasticity = {e}')

plt.axvline(1.0, linestyle='--', linewidth=1)
plt.title('Price Elasticity Response Curve')
plt.xlabel('Dynamic Price Signal')
plt.ylabel('Relative Demand Response')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()