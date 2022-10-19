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
        else:
            amount = int(amount) - 1
            break

    return amount

def discordBot():

    client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
    token = "MTAyNzE3MTgxMDI3NTQ5NTk5OA.Gy01yX.KaKw1kduRRYq_JfTYhxVcSajXEXYsNzxWIoSlg"

    @client.event
    async def on_ready():
        await client.change_presence(status=discord.Status.online, activity=discord.Game('Checking stock... | .sc'))
        print("Bot is ready")

    main(client)

    client.run(token)

def main(client):

    @client.command()
    async def sg(ctx, *, args):

        r = requests.Session()
        response = r.get(args)
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
        priceEUR = int(price) / 24.5
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
        for context_index in range(0, len(sizes_name)):

            if int(stock[context_index]) <= 2:
                color = ":green_circle: "
            elif int(stock[context_index]) <= 4:
                color = ":orange_circle: "
            elif int(stock[context_index]) >= 5:
                color = ":red_circle: "

            msg = msg + str(color) + sizes_name[context_index] + " [" + str(stock[context_index]) + "]\n"

        price = str(priceCZK) + " ~ " + str(priceEUR)
        payout = payoutCZK + " ~ " + payoutEUR
        embed = discord.Embed(title=title, url=args, colour=discord.Color.dark_grey())
        embed.set_thumbnail(url=img)
        embed.add_field(name="Sizes", value=msg, inline=True)
        embed.add_field(name="Price", value=price, inline=True)
        embed.add_field(name="Payout", value=payout, inline=True)
        embed.set_footer(text="SneakerGallery Stock Checker",
                         icon_url="https://cdn.myshoptet.com/usr/www.sneakergallery.cz/user/logos/bilapruh_copy.png")
        await ctx.send(embed=embed)

    @client.command()
    async def sc(ctx, *, args):

        r = requests.session()
        response = r.get(args)
        parser = BeautifulSoup(response.content, "html.parser")
        form = parser.find("form", class_="variations_form cart xt_woovs-single-product")
        img = parser.find("img", class_="wp-post-image")["data-src"]
        title = parser.find("meta", property="og:title")["content"]
        price = parser.find("meta", property="product:price:amount")["content"]
        product_variants = json.loads(form["data-product_variations"])
        msg = ""

        payout = int(price) * 0.85
        payout = round(payout)
        payout = str(payout) + " CZK"
        for size in product_variants:

            size_name = size["attributes"]["attribute_pa_velikost"]
            stock = size["max_qty"]

            if int(stock) <= 2:
                color = ":green_circle: "
            elif int(stock) <= 4:
                color = ":orange_circle: "
            elif int(stock) >= 5:
                color = ":red_circle: "

            msg += str(color) + str(size_name) + " [" + str(stock) + "]" + "\n"

        price = str(price) + " CZK"

        embed = discord.Embed(title=title, url=args, colour=discord.Color.blue())
        embed.set_thumbnail(url=img)
        embed.add_field(name="Sizes", value=msg, inline=True)
        embed.add_field(name="Price", value=price, inline=True)
        embed.add_field(name="Payout", value=payout, inline=True)
        embed.set_footer(text="Section Prague Stock Checker",
                         icon_url="https://sectionstore.cz/wp-content/uploads/2020/02/male_logo.png")
        await ctx.send(embed=embed)

if __name__ == '__main__':
    discordBot()


