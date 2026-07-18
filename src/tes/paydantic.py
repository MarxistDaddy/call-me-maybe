from pydantic import BaseModel, Field
import sys


class test(BaseModel):
    rang: str = Field(min_length=2, max_length=10)
    name: str
    age: int
    job: bool


def main():
    try:
        ist = test(
            rang = "21",
            name = "atlas",
            age = 19,
            job = 13
        )
    except Exception as e:
        print(f"[ERROR] {e.errors()[0]['msg']}")
        return

    print(ist.rang)
    print(ist.name)
    print(ist.age)
    print(ist.job)

if __name__ == "__main__":
    main()

