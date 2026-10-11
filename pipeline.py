import etl, report

if __name__ == '__main__':
    etl.load(etl.transform(etl.extract()))
    report.run()