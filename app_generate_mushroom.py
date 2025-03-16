import streamlit as st
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from PIL import Image, ImageFilter
from src.show_activations_vae import get_activations_model, get_layer_activations
from tensorflow.keras import layers, models 
from tensorflow.keras.utils import plot_model
import io
# import potrace


# Define a function to load the model and apply caching
@st.cache_resource
def load_keras_model():
    try:
        # Attempt to load the Keras model
        generator = load_model('trained_decoder_VAE_mushroom_finalANNEAL.h5')
        return generator
    except Exception as e:
        # Handle any errors that may occur during model loading
        st.error(f"Error loading the model: {e}")
        raise e  # Re-raise the exception after logging it
    
# Function to generate and display the dragon
def generate_mushroom():
    latent_dim = 100  # Latent space size for the generator
    # noise = np.random.normal(0, 1, (1, latent_dim))  # Generate random noise for the latent vector
    generated_image = generator.predict(latent_vector)  # Generate the image using the generator
    generated_image = (generated_image + 1) / 2.0  # Scale from [-1, 1] to [0, 1]
    generated_image = np.clip(generated_image, 0.0, 1.0)  # Clip values to be in [0, 1]

    # Adjust the color of the generated dragon
    mushroom_image = generated_image[0, :, :, 0]  # Get the single generated image (28x28)

    # Convert the color from hex to RGB
    hex_color = color.lstrip('#')
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Color the image by applying the selected color
    colored_image = np.stack([mushroom_image * (rgb_color[0] / 255),  # Red channel
                              mushroom_image * (rgb_color[1] / 255),  # Green channel
                              mushroom_image * (rgb_color[2] / 255)], axis=-1)  # Blue channel
    
    # Convert to PIL Image
    image_pil = Image.fromarray((colored_image * 255).astype(np.uint8))

    # Step 2: Apply Sharpening filter using PIL
    sharpness_filter = ImageFilter.UnsharpMask(radius=8, percent=200, threshold=1)
    sharpened_image = image_pil.filter(sharpness_filter)

    # Create a plot figure
    fig, ax = plt.subplots(figsize=(1, 1))  
    plt.gcf().set_facecolor('black')
    ax.imshow(sharpened_image)
    ax.axis('off')  # Turn off axis
    # Display the image in Streamlit
    fig.patch.set_facecolor('none')  # Set the figure background to transparent
    ax.patch.set_facecolor('none')   # Set the axes background to transparent
    st.pyplot(fig,use_container_width=True)


# Load the model into session state if it is not already there
if 'generator' not in st.session_state:
    try:
        st.session_state.generator = load_keras_model()
    except Exception:
        st.stop()  # Stop execution if the model loading failed

# Access the model from session state
generator = st.session_state.generator

# Streamlit UI
st.title("Got vectors? Create mushrooms.")

st.markdown("""
    **Hello! I'm a model designed to generate mushroom sketches** 🍄

    Using just one latent vector - **two numbers**, I can create a unique mushroom sketch! These two numbers control the **latent space** of the model, which can be easily manipulated to control key features of the mushroom.

    #### What you can do:
    - Adjust the first number to change the **cap size**.
    - Adjust the second number to control the **stem length**.
    - Watch how these two numbers combine to generate completely different mushroom designs.

""")

col1, col2, col3 = st.columns([0.5, 0.1, 0.4])

with col1:
    # Color picker to choose the dragon color
    color = st.color_picker("Choose the mushrooms's color", "#FFFFFF")  # Default color blue

    hat_size = st.slider("Choose :red[$z_1$] (~the mushrooms's cap size)",-3.0, 3.0, 0.0, 0.05)  # Hat size slider
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; margin-top: -20px;">
            <span>Small</span>
            <span>Large</span>
        </div>
        """, unsafe_allow_html=True
    )

    # Add more vertical space
    st.markdown("<br>", unsafe_allow_html=True)  

    leg_size = st.slider("Choose :red[$z_2$] (~the mushrooms's stem length)", -3.0, 3.0, 0.0, 0.05)  # Leg size slider
    st.markdown(
    """
    <div style="display: flex; justify-content: space-between; margin-top: -20px;">
        <span>Short</span>
        <span>Long</span>
    </div>
    """, unsafe_allow_html=True
)

    # Generate the latent vector
    latent_vector = np.array([-(hat_size), -(leg_size)])
    # Reshape it to (1, 2) to represent a batch of size 1 with 2 dimensions
    latent_vector = latent_vector.reshape(1, 2)  # Shape becomes (1, 2)

with col3:
    # Add more vertical space
    # st.markdown("<br> <br>", unsafe_allow_html=True)  
    latex_str = r"\left( \begin{matrix} \color{red}z_1" r" \\ " r"\color{red}z_2 \end{matrix} \right) =   \left( \begin{matrix} \color{red}" + str(hat_size) + r" \\ \color{red}" + str(leg_size) + r" \end{matrix} \right)"
    st.latex(latex_str)
    generate_mushroom()
    
# Add more vertical space
st.markdown("<br>", unsafe_allow_html=True)  

# Create a grid of points (latent space)
x = np.linspace(-3, 3, 100)  # Range of values for latent dimension 1
y = np.linspace(-3, 3, 100)  # Range of values for latent dimension 2
x_grid, y_grid = np.meshgrid(x, y)

# Define the standard Gaussian function (mean=0, std=1)
def gaussian_2d(x, y, sigma=1):
    return (1 / (2 * np.pi * sigma**2)) * np.exp(-0.5 * (x**2 + y**2) / sigma**2)

# Compute the Gaussian PDF for each point in the grid
z = gaussian_2d(x_grid, y_grid)

# Create the contour plot
fig, ax = plt.subplots(figsize=(6, 6))
cp = ax.contour(x_grid, y_grid, z, levels=10, cmap='gray')

# Add labels and title
ax.set_xlabel('$z_1$', color='red')
ax.set_ylabel('$z_2$', color='red')
ax.set_title('Contour plot of latent space', color='white')
fig.patch.set_facecolor('black')  # Set the figure background to transparent
ax.patch.set_facecolor('none')

# Set the color of the axis ticks to white
ax.tick_params(axis='both', colors='white')

# Show the point (z1, z2) on the plot
ax.scatter(hat_size, leg_size, color='red', s=100, label=f'Point ({hat_size}, {leg_size})')  # Add the point in red

# Annotate the point with its coordinates
ax.annotate(f'({hat_size}, {leg_size})', (hat_size, leg_size), textcoords="offset points", xytext=(0, 10), ha='center', color='white')

# Add a color bar to show the density
# fig.colorbar(cp)

# Show the plot in Streamlit
st.pyplot(fig)
st.markdown("<br>", unsafe_allow_html=True) 

show_details = st.toggle("See how the mushroom is decoded from the vector")

if show_details:
    st.write("The latent vector passes through six layers in the decoding process to generate a mushroom image. Each layer contributes to gradually transforming the latent vector into a full-sized image. Let's inspect each layer in detail.")

    # Get activations for each layer in the model
    model = generator

    activation_model = get_activations_model(model)
    activations = get_layer_activations(activation_model, latent_vector)

    # Display the activations and layer descriptions in Streamlit
    for i, layer_activation in enumerate(activations):
        st.write(f"### Layer {i + 1}: {model.layers[i].name}")
        
        # Show a description of the layer
        if isinstance(model.layers[i], layers.InputLayer):
            st.write("The input layer receives the latent vector. This is the starting point for the decoder model.")
        if isinstance(model.layers[i], layers.Dense):
            st.write("This is a Dense layer that performs a fully connected transformation. It expands latent vector into a higher-dimensional tensor suitable for the next layers.")
        elif isinstance(model.layers[i], layers.Reshape):
            st.write("This is a reshape layer. It converts the output of the Dense layer into a 3D shape (height, width, channels), preparing it for the convolutional operations that follow. ")
        elif isinstance(model.layers[i], layers.Conv2DTranspose):
            st.write("This is a Conv2DTranspose layer, used for upsampling. It works by applying learned filters to the input tensor, upscaling it while retaining spatial hierarchies. ")
        elif isinstance(model.layers[i], layers.Conv2D):
            st.write("This is a Conv2D layer used for the final output (image reconstruction).")
        
        # Show the shape of activations (for debugging or analysis)
        # st.write(f"Activation shape: {layer_activation.shape}")

        # Visualization for Layer 1 (input_2) - 2D vector
        if i == 0:  # Layer 1 - Input Layer (Activation shape: (1, 2))
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.imshow(layer_activation[0, :].reshape(1, -1), cmap='gray', aspect='auto')

            ax.text(0.1, 0.0, f"{layer_activation[0, 0]:.2f}", ha='center', va='center', color='red', fontsize=12)
            ax.text(0.9, 0.0, f"{layer_activation[0, 1]:.2f}", ha='center', va='center', color='red', fontsize=12)

            ax.axis('off')  # Turn off axes
            fig.patch.set_facecolor('none')  # Set the figure background to transparent
            ax.patch.set_facecolor('none')   # Set the axes background to transparent
            st.pyplot(fig)
        
        # Visualization for Layer 2 (dense_3) - 1D vector (6272 activations)
        if i == 1:  # Layer 2 - Dense Layer (Activation shape: (1, 6272))
            fig, ax = plt.subplots(figsize=(12, 2))
            ax.imshow(layer_activation[0, :].reshape(1, -1), cmap='gray', aspect='auto')
            ax.axis('off')  # Turn off axes
            fig.patch.set_facecolor('none')  # Set the figure background to transparent
            ax.patch.set_facecolor('none')   # Set the axes background to transparent
            st.pyplot(fig)
        
        # Plot the activations for Layer 3 (index 2), Layer 4 (index 3), and Layer 5 (index 4)
        if i == 2:  # Layer 3 - Reshape Layer (128 filters)
            num_filters = layer_activation.shape[-1]  # Number of filters
            grid_size = 12  # Grid size for 128 filters (12x12 grid)

            # Create the grid with sufficient size
            fig, axes = plt.subplots(grid_size, grid_size, figsize=(15, 15))

            axes = axes.flatten()  # Flatten axes for easier iteration

            for j in range(num_filters):  # Loop over each filter
                ax = axes[j]
                ax.imshow(layer_activation[0, :, :, j], cmap='gray')
                ax.axis('off')

            # Hide unused subplots if there are any
            for j in range(num_filters, len(axes)):
                axes[j].axis('off')

            fig.patch.set_facecolor('none')  # Set the figure background to transparent
            ax.patch.set_facecolor('none')   # Set the axes background to transparent
            st.pyplot(fig)

        if i == 3:  # Layer 4 - Conv2DTranspose Layer (128 filters)
            num_filters = layer_activation.shape[-1]  # Number of filters
            grid_size = 12  # Grid size for 128 filters (12x12 grid)

            # Create the grid with sufficient size
            fig, axes = plt.subplots(grid_size, grid_size, figsize=(15, 15))

            axes = axes.flatten()  # Flatten axes for easier iteration

            for j in range(num_filters):  # Loop over each filter
                ax = axes[j]
                ax.imshow(layer_activation[0, :, :, j], cmap='gray')
                ax.axis('off')

            # Hide unused subplots if there are any
            for j in range(num_filters, len(axes)):
                axes[j].axis('off')
            fig.patch.set_facecolor('none')  # Set the figure background to transparent
            ax.patch.set_facecolor('none')   # Set the axes background to transparent
            st.pyplot(fig)

        if i == 4:  # Layer 5 - Conv2DTranspose Layer (64 filters)
            num_filters = layer_activation.shape[-1]  # Number of filters
            grid_size = 8  # Grid size for 64 filters (8x8 grid)

            # Create the grid with sufficient size
            fig, axes = plt.subplots(grid_size, grid_size, figsize=(15, 15))

            axes = axes.flatten()  # Flatten axes for easier iteration

            for j in range(num_filters):  # Loop over each filter
                ax = axes[j]
                ax.imshow(layer_activation[0, :, :, j], cmap='gray')
                ax.axis('off')

            # Hide unused subplots if there are any
            for j in range(num_filters, len(axes)):
                axes[j].axis('off')
            fig.patch.set_facecolor('none')  # Set the figure background to transparent
            ax.patch.set_facecolor('none')   # Set the axes background to transparent
            st.pyplot(fig)

            # Visualization for Layer 6 (conv2d_4) - Final output layer (Activation shape: (1, 28, 28, 1))
        if i == 5:  # Layer 6 - Final Conv2D layer (Activation shape: (1, 28, 28, 1))
            final_activation = layer_activation[0, :, :, 0]  # Extract the (28, 28) image from the 4D output
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(final_activation, aspect='auto', cmap='gray')  
            ax.axis('off')  # Turn off axes
            fig.patch.set_facecolor('none')  # Set the figure background to transparent
            ax.patch.set_facecolor('none')   # Set the axes background to transparent
            st.pyplot(fig)

# Instructions
st.markdown("Would create a better model? have any other suggestions? Please inform the author who is eager to learn :)")

# HTML Form to send data to Formspree
contact_form = """
<form
  action="https://formspree.io/f/xzzezrqe"
  method="POST"
>
  <label>
    Your email:
    </br>
    <input type="email" name="email">
  </label>
  </br>
  <label>
    Your message:
    </br>
    <textarea name="message"></textarea>
  </label>
  <!-- your other form fields go here -->
  <button type="submit">Send</button>
</form>
"""

# Display the form in Streamlit
st.markdown(contact_form, unsafe_allow_html=True)