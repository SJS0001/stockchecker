import requests, discord, json
from discord.ext import commands
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def square(size_variants):

    amount = 1
    while True:

        r = requests.Session()

        data = {
            "productId": productId,
            "priceId": priceId,
            "language": "cs",
            "parameterValueId[5]": size_variants,
            "amount": str(amount),
        }

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.sneakergallery.cz",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "x-shoptet-xhr": "Shoptet_Coo7ai"
        }

        atc = r.post("https://www.sneakergallery.cz/action/Cart/addCartItem/", data=data, headers=headers).json()
        code = atc["code"]

        if code == 200:
            amount = int(amount) + 1
            if amount == 20:
                return amount
        else:
            amount = int(amount) - 1
            break

    return amount

def discordBot():
    try:
        client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
        token = ""

        @client.event
        async def on_ready():
            await client.change_presence(status=discord.Status.online, activity=discord.Game('Checking stock... | .sc / .sg'))
            print("Bot is ready")

        main(client)

        client.run(token)
    except:
        discordBot()


def main(client):

    @client.command()
    async def sg(ctx, *, message):

        r = requests.Session()
        response = r.get("https://api.exchangerate.host/latest?base=EUR").json()
        if response["success"] == True:
            czRate = response["rates"]["CZK"]
        else:
            print("Exchange rate api is dead, using default set 24.5czk...")
            czRate = 24.5

        if message.startswith("https://"):
            url = message
        else:
            search = r.get(f"""https://www.sneakergallery.cz/vyhledavani/?string={message}""")
            searchParser = BeautifulSoup(search.content, "html.parser")
            try:
                productNameSearch = searchParser.find("a", attrs={"data-micro": "url"})["href"]
                url = "https://www.sneakergallery.cz" + str(productNameSearch)
            except:
                print("Wrong keywords given.")
        try:
            response = r.get(url)
            parser = BeautifulSoup(response.content, "html.parser")
            global productId
            global priceId
            productId = parser.find("input", attrs={"name": "productId"})["value"]
            priceId = parser.find("input", attrs={"name": "priceId"})["value"]
            scrapeSizes = parser.find("select", attrs={"class": "hidden-split-parameter parameter-id-5"})
            img = parser.find("meta", attrs={"property": "og:image"})["content"]
            title = parser.find("meta", attrs={"property": "og:title"})["content"]
            price = parser.find("span", attrs={"class": "price-final-holder"}).get_text()
            price = price.replace("Kč", "")
            price = price.replace(" ", "")
            price = price.strip()
    
            priceCZK = str(price) + " CZK"
            priceEUR = int(price) / czRate
            payoutCZK = int(price) * 0.85
            payoutEUR = int(priceEUR) * 0.85

            priceEUR = round(priceEUR)
            payoutCZK = round(payoutCZK)
            payoutEUR = round(payoutEUR)

            priceEUR = str(priceEUR) + " EUR"
            payoutCZK = str(payoutCZK) + " CZK"
            payoutEUR = str(payoutEUR) + " EUR"
            variants = scrapeSizes.find_all("option")

            size_variants = []
            sizes_name = []
            stock = []

            for id in variants:
                soup = BeautifulSoup(str(id), 'html.parser')
                add = soup.find("option")["value"]
                sizess = soup.get_text()

                if add != "":
                    size_variants.append(add)
                if sizess != "Zvolte variantu":
                    sizes_name.append(sizess)

            with ThreadPoolExecutor(max_workers=50) as executor:

                results = executor.map(square, size_variants)

            for result in results:
                stock.append(result)

            msg = ""
            global totalStockSg
            totalStockSg = 0

            for context_index in range(0, len(sizes_name)):
                
                totalStockSg += int(stock[context_index])

                if int(stock[context_index]) == 0:
                    color = ":purple_circle: "
                elif int(stock[context_index]) <= 2:
                    color = ":green_circle: "
                elif int(stock[context_index]) <= 4:
                    color = ":orange_circle: "
                elif int(stock[context_index]) >= 5:
                    color = ":red_circle: "

                msg = msg + str(color) + sizes_name[context_index] + " [" + str(stock[context_index]) + "]\n"

            price = str(priceCZK) + " ~ " + str(priceEUR)
            payout = payoutCZK + " ~ " + payoutEUR
            embed = discord.Embed(title=title, url=url, colour=discord.Color.dark_grey())
            embed.set_thumbnail(url=img)
            embed.add_field(name="Sizes", value=msg, inline=True)
            embed.add_field(name="Price", value=price, inline=True)
            embed.add_field(name="Payout", value=payout, inline=True)
            embed.add_field(name="Total Stock", value=totalStockSg, inline=True)
            if int(stock[context_index]) >= 19:
                embed.add_field(name="Stock", value="Stock Unlimited.", inline=True)
            embed.set_footer(text="SneakerGallery Stock Checker",
                            icon_url="https://cdn.myshoptet.com/usr/www.sneakergallery.cz/user/logos/bilapruh_copy.png")
            await ctx.send(embed=embed)
            print("Checked stock with link or kws: " + url)
        except:
            await ctx.send(f"Wrong keywords given.")

    @client.command()
    async def sc(ctx, *, args):
        
        r = requests.session()

        if args.startswith("https://"):
            url = args
        else:
            search = r.get(f"""https://sectionstore.cz/?s={args}&post_type=product""")
            searchParser = BeautifulSoup(search.content, "html.parser")
            try:
                productNameSearch = searchParser.find("span", attrs={"class": "gtm4wp_productdata"})["data-gtm4wp_product_url"]
                url = productNameSearch
            except:
                print("Wrong keywords given.")
        try:
            response = r.get(url)
            parser = BeautifulSoup(response.content, "html.parser")
            form = parser.find("form", class_="variations_form cart")
            img = parser.find("img", class_="wp-post-image")["data-src"]
            title = parser.find("meta", property="og:title")["content"]
            price = parser.find("meta", property="product:price:amount")["content"]
            product_variants = json.loads(form["data-product_variations"])

            msg = ""

            payout = int(price) * 0.85
            payout = round(payout)
            payout = str(payout) + " CZK"
            global totalStockSc
            totalStockSc = 0

            for size in product_variants:

                size_name = size["attributes"]["attribute_pa_velikost"]
                stock = size["max_qty"]
                
                totalStockSc += int(stock)
                if int(stock) <= 2:
                    color = ":green_circle: "
                elif int(stock) <= 4:
                    color = ":orange_circle: "
                elif int(stock) >= 5:
                    color = ":red_circle: "

                msg += str(color) + str(size_name) + " [" + str(stock) + "]" + "\n"

            print(totalStockSc)
            price = str(price) + " CZK"

            embed = discord.Embed(title=title, url=url, colour=discord.Color.blue())
            embed.set_thumbnail(url=img)
            embed.add_field(name="Sizes", value=msg, inline=True)
            embed.add_field(name="Price", value=price, inline=True)
            embed.add_field(name="Payout", value=payout, inline=True)
            embed.add_field(name="Total Stock", value=totalStockSc, inline=True)
            embed.set_footer(text="Section Prague Stock Checker",
                            icon_url="https://sectionstore.cz/wp-content/uploads/2020/02/male_logo.png")
            await ctx.send(embed=embed)
            print("Checked stock with link or kws: " + args)
        except:
            await ctx.send(f"Wrong keywords given.")
if __name__ == '__main__':
    discordBot()


