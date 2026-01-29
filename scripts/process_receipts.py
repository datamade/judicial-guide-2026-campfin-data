import sys
import csv
import json
import operator
from dateutil.parser import parse

csv.field_size_limit(sys.maxsize)

TOP_DONOR_COUNT = 5
START_DATE = parse("2026-01-01")
COMMITTEES = [
    "40812",
    "35539",
    "40745",
    "40614",
    "39572",
    "23540",
    "40611",
    "40620",
    "40839",
    "40775",
    "40878",
    "40664",
    "40785",
    "40702",
    "40666",
    "40752",
    "40736",
    "40861",
    "40704",
    "40651",
    "40644",
    "40731",
    "36890",
    "40726",
    "40624",
    "40945",
    "40646",
    "40746",
    "40655",
    "39605",
    "40843",
    "40919",
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
