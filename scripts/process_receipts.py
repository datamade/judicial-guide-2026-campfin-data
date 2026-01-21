import sys
import csv
import json
import operator
from dateutil.parser import parse

csv.field_size_limit(sys.maxsize)

TOP_DONOR_COUNT = 5
START_DATE = parse("2023-01-01")
COMMITTEES = [
    "39423",
    "20812",
    "39337",
    "39440",
    "39624",
    "39519",
    "39445",
    "39509",
    "31848",
    "39454",
    "39444",
    "39442",
    "39459",
    "39357",
    "39716",
    "39441",
    "39452",
    "37023",
    "35497",
    "39468",
    "39572",
    "37090",
    "39688",
    "24137",
    "39485",
    "39568",
    "39463",
    "37002",
    "35501",
    "22396",
    "25568",
    "39508",
    "39515",
    "36987",
    "39511",
    "39401",
    "35453",
    "39493",
    "39437",
    "39531",
    "31878",
    "39623",
    "36795",
    "39582",
    "39328",
    "39692",
    "35789",
    "39555",
    "21557",
    "39596",
    "39577",
    "39467",
    "39604",
    "39522",
    "39675",
    "39672",
    "39299",
    "39537",
    "39592",
    "39560",
    "39704",
    "39575",
    "39605",
    "39561",
    "39559",
]

if __name__ == "__main__":
    input_file = sys.argv[1]  # 'data/raw/receipts-trimmed.txt'

    acc = {}
    for committee in COMMITTEES:
        acc[committee] = {
            "committee": committee,
            "totalContributions": 0,
            "contributions": [],
            "topDonors": [],
        }

    with open(input_file, "r", encoding="latin-1") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")

        # consider trimming earlier dates at front of txt file
        for row in reader:
            committee_id = row["CommitteeID"]

            if (
                row["RcvDate"]
                and (row["Archived"] != "True")
                and (parse(row["RcvDate"]) >= START_DATE)
                and (committee_id in COMMITTEES)
            ):
                receipt_date = parse(row["RcvDate"])
                # tally total contributions across contributors
                acc[committee_id]["totalContributions"] += float(row["Amount"])

                firstName = row["FirstName"].strip()
                lastName = row["LastOnlyName"].strip()
                zipCode = row["Zip"].strip()

                acc[committee_id]["contributions"].append(
                    {
                        "firstName": firstName,
                        "lastName": lastName,
                        "date": row["RcvDate"],
                        "amount": float(row["Amount"]),
                        "occupation": row["Occupation"],
                        "employer": row["Employer"],
                        "zipCode": zipCode,
                        # "fullRow": row,
                    }
                )

                # see if donor is already in topDonors
                # if they are, add to aggregate total
                # if they're not, create a new dict
                donor = next(
                    (
                        x
                        for x in acc[committee_id]["topDonors"]
                        if x["firstName"].strip() == firstName
                        and x["lastName"].strip() == lastName
                        and x["zipCode"].strip() == zipCode
                    ),
                    None,
                )
                if donor:
                    donor["aggregateAmount"] += float(row["Amount"])
                else:
                    acc[committee_id]["topDonors"].append(
                        {
                            "firstName": firstName,
                            "lastName": lastName,
                            "occupation": row["Occupation"],
                            "employer": row["Employer"],
                            "aggregateAmount": float(row["Amount"]),
                            "zipCode": zipCode,
                        }
                    )

        # sort by aggregate donation and slice to top donors
        committeeList = list(acc.values())
        for committee in committeeList:
            committee["topDonors"].sort(
                key=operator.itemgetter("aggregateAmount"), reverse=True
            )
            committee["topDonors"] = committee["topDonors"][:TOP_DONOR_COUNT]

            # also sort individual donations by date
            committee["contributions"].sort(
                key=operator.itemgetter("date"), reverse=True
            )

        print(json.dumps(committeeList, indent=4))
