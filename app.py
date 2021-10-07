import psycopg2, csv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database stuff - we can probably comment this out at this point
try:
    conn = psycopg2.connect(
        host="ec2-54-170-163-224.eu-west-1.compute.amazonaws.com",
        database="de4fdaf8osb01c",
        user="epsxuyzwewbnlj",
        password="bfd54096dbb405f667865b7c0cc632161c41e4b1773cbd656057dcc537f7788f")
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


def sqltest():
    cur = conn.cursor()

    # execute a statement
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    print(db_version)

    # close the communication with the PostgreSQL
    cur.close()
    return "Database status: UP, Database Version: " + str(db_version)


# Loading in data for a fresh API call - reliable but inefficient, may not need to be fixed
def load_data():
    with open("GHG_averages.csv") as file:
        reader = csv.reader(file)
        country_data = list(reader)

    for line in country_data:
        if line == []:
            country_data.remove(line)

    with open("Calc_info.csv") as file:
        reader = csv.reader(file)
        calc_data = list(reader)

    return country_data, calc_data


@app.route("/")
@cross_origin()
def helloWorld():
    sqltest()
    return "Hello, cross-origin-world!"


@app.route('/getmsg/', methods=['GET'])
@cross_origin()
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {"message": f"Hello {name}"}

    # Return the response in json format
    return jsonify(response)


@app.route('/healthcheck/', methods=['GET'])
@cross_origin()
def health():
    dbhealth = sqltest();
    response = {"health-status": f"{dbhealth}"}
    return jsonify(response)


@app.route('/env-data/', methods=['GET'])
@cross_origin()
def footprintcalc():
    # Loading data using the load data function, country data has country averages, calc data has calculations
    country_data, calc_data = load_data()

    # Finding the average carbon emissions for the country selected
    country = request.args.get('Country', None)
    for a in range(len(country_data)):
        if country_data[a][0] == country:
            average = float(country_data[a][1])
            break
    else:
        raise NotImplementedError(
            "This country is not yet implemented within our calculator, please report this error to us by"
            "raising an error on our github page!")

    # Calculating food emissions based upon meat diet
    meat_consumption = int(request.args.get('Food1', None))
    food_em = int(calc_data[meat_consumption][1])/100

    # Adjusting food emissions based upon local sourcing
    local_source_ns = bool(request.args.get('Check1', None))
    if local_source_ns:
        local_sourcing = 50
    else:
        local_sourcing = int(request.args.get('Food2', None))
    food_em = food_em - food_em * local_sourcing/1000

    # Calculating transport emissions based upon primary means of travel
    vehicle = int(request.args.get('Transport1', None))
    if vehicle != 1:
        transport_em = int(calc_data[14+vehicle][1])/100
    else:
        transport_em = 0

    # Calculating air travel emissions based upon number of flights (round-trip)
    domestic = int(request.args.get('Flights1', None))
    domestic = domestic * int(calc_data[35][1]) * 2
    twelve_fifty = int(request.args.get('Flights2', None))
    twelve_fifty = twelve_fifty * int(calc_data[36][1]) * 2
    twentyfive_hundo = int(request.args.get('Flights3', None))
    twentyfive_hundo = twentyfive_hundo * int(calc_data[37][1]) * 2
    fiftyfive_hundo = int(request.args.get('Flights4', None))
    fiftyfive_hundo = fiftyfive_hundo * int(calc_data[38][1]) * 2
    ninety_hundo = int(request.args.get('Flights5', None))
    ninety_hundo = ninety_hundo * int(calc_data[39][1]) * 2
    seventeen_five_hundo = int(request.args.get('Flights6', None))
    seventeen_five_hundo = seventeen_five_hundo * int(calc_data[40][1]) * 2

    flights_em = domestic + twelve_fifty + twentyfive_hundo + fiftyfive_hundo + ninety_hundo + seventeen_five_hundo
    flights_em = flights_em/1000
    # This fucks it all up
    #private_flyer = bool(request.args.get('Flights7', None))
    #if private_flyer:
     #   flights_em += 100000000

    # Calculating home emissions based upon house type
    house = int(request.args.get('House1', None))
    home_em = int(calc_data[house+9][1])/100

    # Adjusting home emissions based upon people in the home
    adults = int(request.args.get('House4', None))
    home_em = home_em - (adults-1) * 0.07

    # Calculating energy emissions based upon energy mix
    energy_ns = bool(request.args.get('Check2', None))
    if energy_ns:
        energy = 30
    else:
        energy = int(request.args.get('House2', None))
    energy_em = int(calc_data[22][1])/100
    energy_em = energy_em - energy/100 * energy_em

    # Adjusting energy emissions based upon energy-saving implements
    esavers = int(request.args.get('House3', None))
    if esavers == 0:
        energy_saved = 3
    else:
        energy_saved = int(calc_data[26+esavers][1])
    energy_em = energy_em - energy_saved/100

    # Calculating if anything is much above or below average for every single category
    if food_em >= int(calc_data[2][1])/100 + 0.05:
        food_average = 'Above average'
    elif food_em <= int(calc_data[2][1])/100 - 0.05:
        food_average = 'Below average'
    else:
        food_average = 'Average'

    if home_em >= int(calc_data[11][1])/100 + 0.08*(adults-1):
        home_average = 'Above average'
    elif home_em <= int(calc_data[11][1])/100 - 0.05*(adults-1):
        home_average = 'Below average'
    else:
        home_average = 'Average'

    if transport_em >= int(calc_data[17][1])/100 + 0.05:
        transport_average = 'Above average'
    elif transport_em <= int(calc_data[17][1])/100 - 0.05:
        transport_average = 'Below average'
    else:
        transport_average = 'Average'

    if energy_em >= int(calc_data[23][1])/100:
        energy_average = 'Above average'
    elif energy_em <= int(calc_data[23][1])/100 - 0.1:
        energy_average = 'Below average'
    else:
        energy_average = 'Average'

    if flights_em >= 0.3:
        flights_average = 'Above average'
    elif flights_em <= 0.13:
        flights_average = 'Below average'
    else:
        flights_average = 'Average'

    # Calculating the final emissions total for the user
    total_em = food_em + transport_em + home_em + energy_em
    total_em *= average
    total_em += flights_em

    # Turning the total emissions into a footprint score
    print(total_em)
    print(flights_em)
    print(average)
    if total_em >= average * 1.5:
        footprint = 1
        print(footprint)
    elif total_em <= average * 0.6:
        footprint = 0.05
        print(footprint)
    else:
        footprint = (total_em-average)/average + 0.5
        print(footprint)

    # Returning the carbon footprint to the site
    response = {"footprintScore": footprint}
    return jsonify(response)
