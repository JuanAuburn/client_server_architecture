#include <algorithm>
#include <limits>
#include <vector>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <ctime>
#include <cstdlib>
#include <thread>
using namespace std;

using Point = std::vector<double>;
using DataFrame = std::vector< Point >;

// Info to random means
double min_value_for_random = std::numeric_limits<double>::max();
double max_value_for_random = 0;
int dimension = 0;

Point split(std::string str, char delim = ',') {
	Point data;
	std::string sub_str;
	int start_position = 0;
	int len = 0;
	for (int x = 0; x < str.size(); x++) {
    	if (str[x] == delim) {
    		if (len > 0) {
    			sub_str = str.substr(start_position, len);
    			std::string::size_type sz;
				double value = std::stof(sub_str,&sz);
				if(value > max_value_for_random) {
					max_value_for_random = value;
				}
				if(value < min_value_for_random) {
					min_value_for_random = value;
				}
				data.push_back(value);
			}
    		start_position = x+1;
    		len = 0;
		} else {
			len++;
		}
    }
    if(dimension == 0) {
    	dimension = data.size();
	} else {
		if(dimension != data.size()){
			cout<<"ERROR - in the data set, the dimensions in the dataset no is equal"<<endl;
			exit(0);
		}
	}
    return(data);
}

DataFrame dataSet(char filename[]) {
	DataFrame data;
	std::ifstream infile(filename);
	std::string line;
	while (std::getline(infile, line))
	{
		Point subvector = split(line, ',');
		data.push_back(subvector);
	}
	return(data);
}

void printVector(std::vector<auto> vector) {
	for (int x = 0; x < vector.size(); x++) {
		cout<<vector[x]<<", ";
    }
	cout<<endl;
}

void printMatrix(DataFrame matrix) {
	for (int x = 0; x < matrix.size(); x++) {
		printVector(matrix[x]);
    }
}

double square(double value) {
	return value * value;
}

double squared_l2_distance(Point first, Point second) {
	double total = 0;
	for (int i = 0; i < first.size(); i++) {
		total = total + square(first[i] - second[i]);
    }
	return(total);
}

double fRand()
{
    double f = (double)rand() / RAND_MAX;
    return min_value_for_random + f * (max_value_for_random - min_value_for_random);
}

Point random_point() {
	Point point;
	for (int i = 0; i < dimension; i++) {
		point.push_back(fRand());
	}
	return(point);
}

DataFrame random_means(int k) {
	cout<<"START random_means -----------------------------------------"<<endl;
	DataFrame means;
	for (int i = 0; i < k; i++) {
		means.push_back(random_point());
	}
	printMatrix(means);
	cout<<"END random_means -------------------------------------------"<<endl;
	return(means);
}

void p_k_means(const DataFrame& data, int k, int number_of_iterations, DataFrame means, double *bs_distances, std::vector<int> *bs_assignments, DataFrame *bs_means) {
	
	for (int iteration = 0; iteration < number_of_iterations; iteration++) {
		std::vector<int> assignments(data.size());
		double assignments_best_distances = 0;
		int now_iteration = iteration+1;
		// cout<<"START iteration: "<<now_iteration<<" -----------------------------------------"<<endl;
		// Find assignments.
		// cout<<"START assignments -----------------------------------------"<<endl;
		for (int point = 0; point < data.size(); point++) {
			double best_distance = std::numeric_limits<double>::max();
			int best_cluster = 0;
			for (int cluster = 0; cluster < k; cluster++) {
				const double distance = squared_l2_distance(data[point], means[cluster]);
				if (distance < best_distance) {
					best_distance = distance;
					best_cluster = cluster;
				}
			}
			assignments_best_distances += best_distance;
			assignments[point] = best_cluster;
		}
		// printVector(assignments);
		// cout<<"All distances: "<<assignments_best_distances<<endl;
		// cout<<"END assignments -------------------------------------------"<<endl;
		
		if(assignments_best_distances == *bs_distances) {
			iteration = number_of_iterations;
		}
		
		if(assignments_best_distances < *bs_distances) {
			*bs_distances = assignments_best_distances;
			*bs_means = means;
			*bs_assignments = assignments;
		}
	
		// cout<<"START new_means SUM -----------------------------------------"<<endl;
		// Sum up and count points for each cluster.
		DataFrame new_means(means);
		// printMatrix(new_means);
		// cout<<new_means.size()<<endl;
		std::vector<int> counts(k, 0);
		// printVector(counts);
		for (int point = 0; point < data.size(); point++) {
			// printVector(data[point]);
			// cout<<assignments[point]<<endl;
			const int cluster = assignments[point];
			for (int i = 0; i < dimension; i++) {
				new_means[cluster][i] += data[point][i];
			}
			counts[cluster] += 1;
		}
		// printMatrix(new_means);
		// cout<<"END new_means SUM -------------------------------------------"<<endl;
		
		// cout<<"START new_means DIV -----------------------------------------"<<endl;
		// Divide sums by counts to get new centroids.
		for (int cluster = 0; cluster < k; ++cluster) {
			const int count = counts[cluster];
			if(count == 0) {
				// cout<<"The cluster: "<<cluster<<" no is used"<<endl;
				means[cluster] = random_point();
			} else {
				for (int i = 0; i < dimension; i++) {
					means[cluster][i] = new_means[cluster][i] / count;
				}	
			}
		}
		// printMatrix(means);
		// cout<<"END new_means DIV -------------------------------------------"<<endl;
		// cout<<"END iteration: "<<now_iteration<<" -------------------------------------------"<<endl;
	}
}

double g_bs_distances = std::numeric_limits<double>::max();
DataFrame g_bs_means;
std::vector<int> g_bs_assignments;

void k_means(const DataFrame& data, int k, int number_of_iterations, int number_of_threads) {
	cout<<"k_means"<<endl;
	thread myThreads[number_of_threads];
	
	int iterations_thread = number_of_iterations/number_of_threads;
	if (iterations_thread < 1) {
		iterations_thread = number_of_iterations;
		number_of_threads = 1;
	}
	std::vector<double> bs_distances(number_of_threads, std::numeric_limits<double>::max());
	std::vector<DataFrame> bs_means(number_of_threads);
	std::vector< std::vector<int> > bs_assignments(number_of_threads);
	for(int i=0; i<number_of_threads; i++) {
		DataFrame tempMeans = random_means(k);
		myThreads[i] = thread(p_k_means, data, k, iterations_thread, tempMeans, &(bs_distances[i]), &(bs_assignments[i]), &(bs_means[i]));
	}
	
	for (int i=0; i<number_of_threads; i++) {
        myThreads[i].join();
        cout<<"BEST SOLUTION to THREAD: "<<i<<endl;
        cout<<"total distance: "<<bs_distances[i]<<endl;
	  	cout<<"Clusters:"<<endl;
		printMatrix(bs_means[i]);
	  	cout<<"Assignments"<<endl;
  		printVector(bs_assignments[i]);
    }
    
    for (int i=0; i<number_of_threads; i++) {
    	if(bs_distances[i] < g_bs_distances) {
    		g_bs_distances = bs_distances[i];
    		g_bs_means = bs_means[i];
			g_bs_assignments = bs_assignments[i];
		}
    }
}

int main() {
	srand(time(0)); // Initialize random number generator
	DataFrame data = dataSet("iris.data");
	// cout<<"dimension: "<<dimension<<endl;
	k_means(data, 3, 100, 4);
	cout<<"BEST SOLUTION"<<endl;
	cout<<"All distances: "<<g_bs_distances<<endl;
  	cout<<"Clusters:"<<endl;
	printMatrix(g_bs_means);
  	cout<<"Assignments"<<endl;
  	printVector(g_bs_assignments);
	return(0);
}

