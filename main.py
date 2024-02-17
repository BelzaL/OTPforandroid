import os
import secrets
import base64
from PIL import Image as PILImage
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.uix.label import Label

class OTPApp(App):
    def build(self):
        self.title = 'OTP Image Encryption/Decryption'
        self.original_image = Image(allow_stretch=True)
        self.original_image.source = ''  # Set initial source to empty
        self.key_image = Image(allow_stretch=True)
        self.key_image.source = ''  # Set initial source to empty
        self.encrypted_image = Image(allow_stretch=True)
        self.generate_key_button = Button(text='Generate Binary Key', on_press=self.generate_key)
        self.encrypt_button = Button(text='Encrypt/Decrypt', on_press=self.encrypt_image)
        self.filechooser_image = FileChooserIconView(path='.')
        self.filechooser_key_material = FileChooserIconView(path='.')

        layout = BoxLayout(orientation='vertical')

        # Add descriptions for file choosers
        label_image = Label(text="Select Image:")
        label_key_material = Label(text="Select Key Material:")
        
        layout.add_widget(label_image)
        layout.add_widget(self.filechooser_image)
        layout.add_widget(label_key_material)
        layout.add_widget(self.filechooser_key_material)

        layout_buttons = BoxLayout(orientation='horizontal')
        layout_buttons.add_widget(self.generate_key_button)
        layout_buttons.add_widget(self.encrypt_button)

        layout.add_widget(layout_buttons)
        layout.add_widget(self.encrypted_image)

        Window.size = (800, 800)
        return layout


    def generate_key(self, instance):
        key_size = 10000000  # Adjust the size as needed
        binary_key = secrets.token_bytes(key_size)
        key_material_file = 'key_material.bin'
        with open(key_material_file, 'wb') as f:
            f.write(binary_key)

        print(f"Binary key material saved to '{key_material_file}'")
        self.refresh_file_choosers()

    def encrypt_image(self, instance):
        image_path = self.filechooser_image.selection[0]
        
        key_material_path = self.filechooser_key_material.selection[0]

        if not os.path.exists(image_path) or not os.path.exists(key_material_path):
            print("Please select both an image and a key material file.")
            return

        # Load the original image and key material
        with open(image_path, 'rb') as f:
            image_data = f.read()
        with open(key_material_path, 'rb') as f:
            key_data = f.read()

        # Ensure both data have the same length
        if len(image_data) > len(key_data):
            print("Key material is too small. Please generate a new key material.")
            return
        else:
            min_length = min(len(image_data), len(key_data))
            consumed_key_data = key_data[:min_length]
            remaining_key_data = key_data[min_length:]
            image_data = image_data[:min_length]

        # Perform XOR encryption
        encrypted_data = bytes([a ^ b for a, b in zip(image_data, consumed_key_data)])

        # Save encrypted data to a file
        if '_encrypted.' in image_path:
            encrypted_image_path = image_path.replace('_encrypted.', '.')
        else:
            encrypted_image_path = '.'.join(image_path.split('.')[:-1]) + '_encrypted.' + image_path.split('.')[-1]
        
        with open(encrypted_image_path, 'wb') as f:
            f.write(encrypted_data)

        # Save the remaining key material back to the key material file
        with open(key_material_path, 'wb') as f:
            f.write(remaining_key_data)

        # Save the consumed key
        key_filename = os.path.splitext(os.path.basename(image_path))[0] + "_key"
        with open(key_filename, 'wb') as f:
            f.write(consumed_key_data)
        
        # Delete the original image and key material files
        os.remove(image_path)
        if '_encrypted.' in image_path:
            os.remove(key_filename)
        else:
            pass
        
        self.refresh_file_choosers()


    def refresh_file_choosers(self):
        # Clear selections
        self.filechooser_image.selection = []
        self.filechooser_key_material.selection = []

        # Reset paths
        self.filechooser_image.path = '.'
        self.filechooser_key_material.path = '.'
        
        # Trigger file chooser refresh after a small delay to ensure the update
        Clock.schedule_once(self.filechooser_image._update_files)
        Clock.schedule_once(self.filechooser_key_material._update_files)


if __name__ == '__main__':
    OTPApp().run()
