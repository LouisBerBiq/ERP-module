# Getting Started With Odoo

Notes:
- You can use a terminal of your choice (unix or windows shell).
- On Windows&nbsp;: use backslashes (`\`) instead of forward ones (`/`) and absolute paths must start with `C:\`.
- Sections in [square brackets] are to be replaced depending on your environment.

## Setting up
1. Install Docker (or Podman in Docker compatibility mode).<br>
   Start Docker Desktop at least once and accept their license.
2. Clone the docker.io/mvaodoo/odoo_training image&nbsp;: `docker image pull docker.io/mvaodoo/odoo_training`.
3. Run a new container with this image&nbsp;: `docker run -it -d -v odoo_pg_data:/var/lib/postgresql/data -v '[/path/to/parent/directory/of/rental_management/module]':/home/odoo/src/custo:z -p 8069:8069 --name mva_odoo --replace mvaodoo/odoo_training`.
4. Remote connect into the container&nbsp;: `exec -it mva_odoo /bin/bash`.
5. Make sure that everything is up to date and that wkhtmltopdf is installed&nbsp;: `apt update && apt upgrade && apt install wkhtmltopdf`.
6. Once everything is updated & installed&nbsp;: `su odoo`, `cd ~/src/odoo/`.
7. And finally&nbsp;:`./odoo-bin -d my_database --addons-path=/home/odoo/src/custo/`.

You can now connect to `localhost:8069` in your browser.

## Configuration
1. On `localhost:8069`, you will be presented with a login prompt&nbsp;; The credential are `admin` for both field.
2. You will need to install the following modules in from the 'Apps' page&nbsp;: 'sale' (Point de Vente).<br>
   You can also add 'Website' & 'Point of Sale' if you wish to use them.
3. You can switch Odoo's language to french by going to the 9 squares icon in the top left > settings > Languages > Add Languages.<br>
   Then by setting it by going to the top right, on the profile picture, > My Preferences > Language.
4. Also Make sure to set Odoo's Fiscal Localization in settings > Invoicing > Fiscal Localization to your shop's country.

### Store Configuration
The settings page (9 squares icon in the top left > settings) is also where a lot of other settings are configured, here's a few you might want to set up:
- Sales:
  - Product Catalog > Variants > (Attributes)&nbsp;: Add variations attributes (color, size, options, etc…)

## Creating products, adding them to rental & adding categories 
- First, navigate to 9 squares icon in the top left > Sales > Products > Products, and click Create.
- Below the product name are important checkboxes&nbsp;:
  - 'Est un vélo de location' is to make the product available for rental.
  - 'Sales' is to make the product available on the website.
  - 'Point of Sale' is to make the product available on the Point of Sale app.
- The Sales Price, Cost & Rental Price can be set on the first tab. Internal Categories can also be set on this page.
- Attributes & Variants&nbsp;: Once set, variants can be created from the variants integration button at the center top of the page.
- Sales&nbsp;: Do not forget to set 'Is Published' for the product to appear on the website, also set the category of the product as it will appear on the website on this page.
- Point of Sale&nbsp;: Point of Sales have their own categories so don't forget to fill it here too.

### Rental
- 9 squares icon in the top left > Location Vélos
- Here's how to use the rental form:
  1. Draft&nbsp;:
  	- Total Price is calculated based on the bike's rental price and duration of the rental.
  	- Late fee is a fixed amount applied daily.
  2. Rented&nbsp;:
  	- Once confirmed, the rental will be marked as 'rented', a banner will pop at the top whenever it is past the return date.
  	  The return button is at the same place as the rent button.
  2. Returned&nbsp;:
  	- Once the return button clicked, the rental will be done and a new button and an invoice button will be there instead.