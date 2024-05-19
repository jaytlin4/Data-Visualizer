import base64
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import random

def list_files_in_s3_bucket(bucket_name):
    """
    List files in an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :return: List of file names in the bucket.
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)
    files = [obj['Key'] for obj in response['Contents']]
    return files

def download_file_from_s3(bucket_name, file_key, local_dir):
    """
    Download a file from an S3 bucket to a local directory.

    :param bucket_name: Name of the S3 bucket.
    :param file_key: Key (path) of the file in the S3 bucket.
    :param local_dir: Local directory where the file will be downloaded.
    """
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Download the file from S3
        local_path = os.path.join(local_dir, os.path.basename(file_key))
        s3.download_file(bucket_name, file_key, local_path)
        print(f"File downloaded successfully to: {local_path}")
        return local_path
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        sys.exit(1)

def visualize_data(df, output_dir, selected_column, plot_type):
    """
    Visualize the data using matplotlib and return the plot image as a Base64-encoded string.

    :param df: Pandas DataFrame containing the data.
    :param output_dir: Directory where the image file will be saved.
    :param selected_column: Name of the selected column for visualization.
    :param plot_type: Type of plot to generate ('scatter', 'line', 'hist', 'bar', or 'pie').
    :return: Base64-encoded string of the plot image.
    """
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    x_column = df.columns[0]  # First column is always set as x-axis
    y_column = selected_column  # Selected column is set as y-axis

    if plot_type == 'scatter':
        plt.scatter(df[x_column], df[y_column], label=y_column)
    elif plot_type == 'line':
        plt.plot(df[x_column], df[y_column], marker='o', linestyle='-', label=y_column)
    elif plot_type == 'hist':
        plt.hist(df[y_column], bins=10, label=y_column, rwidth=0.8)  # Add a gap between histogram bars
    elif plot_type == 'bar':
        plt.bar(df[x_column], df[y_column], label=y_column)
    elif plot_type == 'pie':
        plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')

    # Set x and y axis labels based on the column names
    plt.xlabel(x_column)
    plt.ylabel(y_column)

    plt.title('Data Visualization')

    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust plot layout
    
    plt.legend()  # Show legend for the line
    
    # Save the plot as an image file
    output_file = os.path.join(output_dir, 'plot.png')
    plt.savefig(output_file)
    plt.close()  # Close the plot to free up memory
    print(f"Plot saved successfully to: {output_file}")
    # Read the saved image file, encode it as Base64, and return the string
    with open(output_file, 'rb') as f:
        image_data = f.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    return base64_image

# Example usage
if __name__ == "__main__":
    # Specify the S3 bucket name and output directory
    bucket_name = os.environ.get('S3_BUCKET_NAME', 'datasetentries')
    output_dir = os.environ.get('OUTPUT_DIR', '/home/ec2-user/AWS_S3_FILES/')

    # List files in the S3 bucket
    files = list_files_in_s3_bucket(bucket_name)

    # Display datasets found for selection
    print("Select a dataset to visualize:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    # Get user input for selected dataset
    while True:
        try:
            dataset_selection = int(input("Enter the number of the dataset: "))
            selected_file = files[dataset_selection-1]
            break
        except (ValueError, IndexError):
            print("Invalid selection. Please enter a valid number.")

    # Download the selected file from S3 to the local directory
    local_path = download_file_from_s3(bucket_name, selected_file, output_dir)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(local_path)

    # Display columns found for selection
    print("Select a column to visualize:")
    for i, column in enumerate(df.columns, start=1):
        print(f"{i}. {column}")

    # Get user input for selected column
    while True:
        try:
            column_selection = int(input("Enter the number of the column: "))
            selected_column = df.columns[column_selection-1]
            break
        except (ValueError, IndexError):
            print("Invalid selection. Please enter a valid number.")

    # Get user input for plot type
    plot_type = input("Enter the type of plot ('scatter', 'line', 'hist', 'bar', or 'pie'): ").lower()
    while plot_type not in ['scatter', 'line', 'hist', 'bar', 'pie']:
        print("Invalid plot type. Please enter 'scatter', 'line', 'hist', 'bar', or 'pie'.")
        plot_type = input("Enter the type of plot ('scatter', 'line', 'hist', 'bar', or 'pie'): ").lower()

    # Perform data visualization and return the Base64-encoded image data
    image_data = visualize_data(df, output_dir, selected_column, plot_type)

    # Now you can use `image_data` to pass the Base64-encoded image data to your frontend
